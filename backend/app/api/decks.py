"""
Decks API

CRUD operations for MTG deck lists.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.utils.database import get_db
from app.utils.security import get_current_user_id
from app.schemas.deck import DeckCreate, DeckUpdate, DeckResponse, DeckListResponse, CardInDeck
from app.models.deck import Deck

router = APIRouter(prefix="/api/decks", tags=["decks"])


@router.get("/", response_model=DeckListResponse)
def list_decks(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    List all decks for the current user.
    
    Returns paginated list of decks.
    """
    # Calculate pagination
    skip = (page - 1) * page_size
    
    # Query decks
    query = db.query(Deck).filter(Deck.user_id == user_id)
    total = query.count()
    decks = query.order_by(Deck.updated_at.desc()).offset(skip).limit(page_size).all()
    
    return DeckListResponse(
        total=total,
        decks=[DeckResponse.from_orm(deck) for deck in decks],
        page=page,
        page_size=page_size
    )


@router.get("/public", response_model=DeckListResponse)
def list_public_decks(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    List public decks (no authentication required).
    """
    skip = (page - 1) * page_size
    
    query = db.query(Deck).filter(Deck.is_public == True)
    total = query.count()
    decks = query.order_by(Deck.updated_at.desc()).offset(skip).limit(page_size).all()
    
    return DeckListResponse(
        total=total,
        decks=[DeckResponse.from_orm(deck) for deck in decks],
        page=page,
        page_size=page_size
    )


@router.post("/", response_model=DeckResponse, status_code=status.HTTP_201_CREATED)
def create_deck(
    deck_data: DeckCreate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Create a new deck.
    """
    # Convert cards to dict format for JSONB storage
    cards_data = [card.dict() for card in deck_data.cards]
    
    # Calculate total card count
    total_cards = sum(card.quantity for card in deck_data.cards)
    card_count = deck_data.card_count or str(total_cards)
    
    # Create deck
    new_deck = Deck(
        user_id=user_id,
        name=deck_data.name,
        description=deck_data.description,
        cards=cards_data,
        card_count=card_count,
        format=deck_data.format,
        colors=deck_data.colors,
        is_public=deck_data.is_public,
        tags=deck_data.tags
    )
    
    db.add(new_deck)
    db.commit()
    db.refresh(new_deck)
    
    return DeckResponse.from_orm(new_deck)


@router.get("/{deck_id}", response_model=DeckResponse)
def get_deck(
    deck_id: UUID,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get a specific deck by ID.
    
    User must own the deck or it must be public.
    """
    deck = db.query(Deck).filter(Deck.id == deck_id).first()
    
    if not deck:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deck not found"
        )
    
    # Check access permissions
    if str(deck.user_id) != user_id and not deck.is_public:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return DeckResponse.from_orm(deck)


@router.put("/{deck_id}", response_model=DeckResponse)
def update_deck(
    deck_id: UUID,
    deck_data: DeckUpdate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Update a deck.
    
    User must own the deck.
    """
    deck = db.query(Deck).filter(Deck.id == deck_id, Deck.user_id == user_id).first()
    
    if not deck:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deck not found"
        )
    
    # Update fields
    update_data = deck_data.dict(exclude_unset=True)
    
    # Convert cards to dict format if provided
    if "cards" in update_data and update_data["cards"] is not None:
        update_data["cards"] = [card.dict() for card in deck_data.cards]
        
        # Recalculate card count
        total_cards = sum(card.quantity for card in deck_data.cards)
        if not deck_data.card_count:
            update_data["card_count"] = str(total_cards)
    
    for field, value in update_data.items():
        setattr(deck, field, value)
    
    db.commit()
    db.refresh(deck)
    
    return DeckResponse.from_orm(deck)


@router.delete("/{deck_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_deck(
    deck_id: UUID,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Delete a deck.
    
    User must own the deck.
    """
    deck = db.query(Deck).filter(Deck.id == deck_id, Deck.user_id == user_id).first()
    
    if not deck:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deck not found"
        )
    
    db.delete(deck)
    db.commit()
    
    return None


@router.post("/{deck_id}/duplicate", response_model=DeckResponse, status_code=status.HTTP_201_CREATED)
def duplicate_deck(
    deck_id: UUID,
    name: Optional[str] = None,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Duplicate an existing deck.
    
    Can duplicate own decks or public decks.
    """
    # Get original deck
    deck = db.query(Deck).filter(Deck.id == deck_id).first()
    
    if not deck:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deck not found"
        )
    
    # Check access permissions
    if str(deck.user_id) != user_id and not deck.is_public:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot duplicate private deck"
        )
    
    # Create duplicate
    new_name = name or f"{deck.name} (Copy)"
    
    new_deck = Deck(
        user_id=user_id,
        name=new_name,
        description=deck.description,
        cards=deck.cards.copy() if deck.cards else [],
        card_count=deck.card_count,
        format=deck.format,
        colors=deck.colors.copy() if deck.colors else None,
        is_public=False,  # Duplicates are private by default
        tags=deck.tags.copy() if deck.tags else None
    )
    
    db.add(new_deck)
    db.commit()
    db.refresh(new_deck)
    
    return DeckResponse.from_orm(new_deck)


@router.post("/import/csv", response_model=DeckResponse, status_code=status.HTTP_201_CREATED)
def import_deck_from_csv(
    name: str,
    csv_content: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Import a deck from CSV content.
    
    CSV format: Card Name,Quantity,Type,Mana Cost,Conditions
    """
    import csv
    import io
    
    cards = []
    reader = csv.DictReader(io.StringIO(csv_content))
    
    for row in reader:
        try:
            card = CardInDeck(
                card_name=row.get("Card Name", "").strip(),
                quantity=int(row.get("Quantity", 1)),
                type=row.get("Type", "").strip() or None,
                mana_cost=row.get("Mana Cost", "").strip() or None,
                conditions=row.get("Conditions", "").strip() or None
            )
            cards.append(card)
        except (ValueError, KeyError) as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid CSV format: {str(e)}"
            )
    
    if not cards:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid cards found in CSV"
        )
    
    # Create deck
    deck_data = DeckCreate(
        name=name,
        cards=cards
    )
    
    return create_deck(deck_data, user_id, db)

