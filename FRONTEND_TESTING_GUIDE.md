# Frontend Testing Guide 🧪

## 🚀 Your Web UI is Ready!

The frontend now has a complete UI for testing user authentication and deck management.

### Access the Application

Open your browser and visit: **http://localhost:5173**

---

## 📋 Testing Checklist

### 1. User Registration ✅

When you first open the app, you'll see a login/register form.

**To Register:**
1. Click "Don't have an account? Register"
2. Fill in the form:
   - **Email**: `yourname@example.com`
   - **Username**: `yourname`
   - **Password**: `yourpassword`
   - **Full Name**: `Your Name`
3. Click "Register"
4. You should see "Registration successful!" and be logged in automatically

**Features to Test:**
- ✅ Form validation (try submitting empty fields)
- ✅ Error messages (try registering with the same username twice)
- ✅ Success message display
- ✅ Automatic login after registration

---

### 2. User Login ✅

**To Login:**
1. If you're on the register form, click "Already have an account? Login"
2. Enter your username and password
3. Click "Login"
4. You should be logged in and see the main dashboard

**Features to Test:**
- ✅ Form validation
- ✅ Error messages (try wrong password)
- ✅ Success message
- ✅ Token storage (check browser localStorage)
- ✅ Persistent login (refresh the page - you should stay logged in)

---

### 3. Create a Deck ✅

Once logged in, you'll see three tabs at the top: **My Decks**, **Create Deck**, and **Profile**.

**To Create a Deck:**
1. Click the "➕ Create Deck" tab
2. Fill in the deck details:
   - **Deck Name**: `My Test Deck`
   - **Description**: `Testing the deck creation feature`
3. Add cards in the text area using this format:
   ```
   4 Lightning Bolt
   20 Mountain
   4 Lava Spike
   4 Chain Lightning
   24 Island
   4 Counterspell
   ```
4. Click "Add These Cards"
5. Verify the cards appear in the "Current Decklist" section
6. Click "Create Deck"
7. You should see "Deck created successfully!" and be redirected to "My Decks"

**Card Format Options:**
- `4 Lightning Bolt` ✓
- `4x Lightning Bolt` ✓
- `1 Black Lotus` ✓

**Features to Test:**
- ✅ Add multiple cards at once
- ✅ Remove individual cards
- ✅ See total card count update
- ✅ Form validation (try creating with no cards)
- ✅ Success message and redirect
- ✅ Card parsing (try different formats)

---

### 4. View Your Decks ✅

After creating decks, click the "📚 My Decks" tab.

**What You'll See:**
- List of all your decks on the left
- Deck details panel on the right
- Total deck count
- Refresh button

**To View Deck Details:**
1. Click on any deck card
2. The right panel will show:
   - Deck name and description
   - Total cards
   - Unique cards
   - Complete decklist
   - Creation date
   - Deck ID

**Features to Test:**
- ✅ Click different decks to switch views
- ✅ See highlighted selected deck
- ✅ View complete decklist
- ✅ See card counts
- ✅ Refresh button updates the list

---

### 5. Delete a Deck ✅

**To Delete:**
1. Go to "📚 My Decks"
2. Find the deck you want to delete
3. Click the "Delete" button on the deck card
4. Confirm the deletion in the popup
5. The deck should disappear from the list

**Features to Test:**
- ✅ Confirmation dialog appears
- ✅ Deck is removed immediately
- ✅ Selected deck view clears if deleted deck was selected
- ✅ Error handling (what happens if deletion fails)

---

### 6. View Profile ✅

Click the "👤 Profile" tab to see your account information.

**What You'll See:**
- User ID (UUID)
- Username
- Email
- Full Name
- Account Status (Active/Inactive badge)
- Verification Status (Verified/Not Verified badge)
- Member Since date

**Features to Test:**
- ✅ All information displays correctly
- ✅ Status badges show correct colors
- ✅ Date formatting

---

### 7. Logout ✅

**To Logout:**
1. Click the "Logout" button in the top-right corner
2. You should be redirected to the login/register page
3. Your session should be cleared

**Features to Test:**
- ✅ Logout clears localStorage
- ✅ Can't access protected pages after logout
- ✅ Need to login again to access app

---

## 🎨 UI Features to Notice

### Visual Design
- ✨ **Modern gradient background** - Blue to indigo gradient
- 🎯 **Clean white cards** - Material design inspired
- 📱 **Responsive layout** - Try resizing your browser
- 🌈 **Status badges** - Color-coded (green = active, yellow = pending, red = error)
- ⚡ **Smooth transitions** - Hover effects and animations
- 📊 **Two-column layout** - Deck list + details view

### User Experience
- ✅ **Real-time validation** - See errors immediately
- ✅ **Success messages** - Green confirmations
- ✅ **Error messages** - Red error alerts
- ✅ **Loading states** - Disabled buttons while processing
- ✅ **Empty states** - Helpful messages when no data
- ✅ **Confirmation dialogs** - Prevent accidental deletions
- ✅ **Auto-redirect** - Smooth navigation flow

---

## 🔍 What to Check in Browser DevTools

### Console (F12)
- No errors should appear
- API calls should complete successfully
- Look for any warnings

### Network Tab
- Watch API calls to `http://localhost:8000`
- Check response status codes (200, 201 for success)
- Inspect request/response payloads

### Application → Local Storage
After logging in, you should see:
- `access_token` - Your JWT token
- `refresh_token` - For token renewal
- `user` - Your user information as JSON

---

## 📝 Test Scenarios

### Scenario 1: New User Journey
1. ✅ Register new account
2. ✅ Create first deck
3. ✅ View deck in list
4. ✅ Check profile
5. ✅ Logout and login again
6. ✅ Verify deck persists

### Scenario 2: Multiple Decks
1. ✅ Create 3 different decks
2. ✅ View each one
3. ✅ Delete one
4. ✅ Create another
5. ✅ Refresh page - all should persist

### Scenario 3: Large Deck
1. ✅ Create a deck with 30+ unique cards
2. ✅ Verify scrolling works in decklist
3. ✅ Check total card count is correct

### Scenario 4: Error Handling
1. ✅ Try to register with existing username
2. ✅ Try to login with wrong password
3. ✅ Try to create deck without cards
4. ✅ Stop backend (`docker-compose stop backend`) and try to create deck
5. ✅ Start backend again and verify recovery

---

## 🐛 Common Issues & Solutions

### Frontend Won't Load
```bash
# Check if frontend is running
docker-compose ps frontend

# Restart frontend
docker-compose restart frontend

# View logs
docker-compose logs frontend
```

### API Calls Failing
```bash
# Check if backend is running
docker-compose ps backend

# Restart backend
docker-compose restart backend

# Check backend logs
docker-compose logs backend
```

### CORS Errors
The backend is configured to allow `http://localhost:5173`. If you see CORS errors:
1. Check browser console for exact error
2. Verify backend is running
3. Check that you're accessing via `localhost:5173` not `127.0.0.1:5173`

### Styling Looks Wrong
```bash
# Rebuild frontend to refresh Tailwind
docker-compose build frontend
docker-compose restart frontend
```

### Can't Create Decks
1. Make sure you're logged in
2. Check browser console for errors
3. Verify backend is running
4. Check if JWT token exists in localStorage
5. Try logging out and back in

---

## 💡 Tips for Testing

1. **Use Browser DevTools** - Keep console open to see errors
2. **Test in Incognito** - Verify fresh user experience
3. **Try Different Browsers** - Chrome, Firefox, Safari
4. **Test Mobile View** - Use DevTools responsive mode
5. **Refresh Often** - Verify data persists
6. **Check Backend Logs** - Watch API calls in real-time:
   ```bash
   docker-compose logs -f backend
   ```

---

## 📊 What's Working vs What's Coming

### ✅ Working Now (Phase 1)
- User Registration
- User Login/Logout
- Create Decks
- View Decks
- Delete Decks
- View Profile
- Token-based Authentication
- Persistent Sessions

### 🔜 Coming in Phase 2
- Run Simulations
- View Simulation Results
- Deck Comparison
- Experiment Framework
- Real-time Progress Updates
- Google OAuth Login
- Deck Editing (inline)
- Deck Sharing
- Public Deck Gallery

---

## 🎯 Success Criteria

You're ready to move to Phase 2 when you can successfully:

- ✅ Register a new account
- ✅ Login with credentials
- ✅ Create multiple decks
- ✅ View all your decks
- ✅ See deck details
- ✅ Delete a deck
- ✅ Logout and login again
- ✅ All data persists after refresh
- ✅ No errors in browser console
- ✅ UI looks good and is responsive

---

## 🚀 Quick Test Commands

```bash
# Check all services are running
docker-compose ps

# Restart everything
docker-compose restart

# View all logs
docker-compose logs -f

# Just backend logs
docker-compose logs -f backend

# Just frontend logs
docker-compose logs -f frontend

# Check API health
curl http://localhost:8000/health
```

---

## 🎉 Happy Testing!

The frontend is fully functional for Phase 1 features. Take your time testing all the functionality before we move on to Phase 2 (Simulation Engine Integration).

**Questions?** Just ask! I'm here to help debug any issues you encounter.

**Found a bug?** That's great! We can fix it before Phase 2.

**Ready for Phase 2?** Let me know and we'll start integrating the simulation engine!

---

## 📸 What You Should See

### Login Screen
- Clean form with email, username, password fields
- Toggle between Login/Register
- Blue gradient background

### Dashboard (After Login)
- Header with welcome message and logout button
- Three tabs: My Decks, Create Deck, Profile
- Clean, modern interface

### My Decks
- Left: Grid of deck cards
- Right: Selected deck details
- Card counts and creation dates

### Create Deck
- Deck name and description fields
- Text area for adding cards
- Live preview of current decklist
- Add/Remove buttons

### Profile
- User information display
- Status badges
- Clean layout

Enjoy testing! 🎮

