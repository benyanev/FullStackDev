import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import TopBar from './components/TopBar';
import Feed from './components/Feed/Feed';
import Users from './components/Users/Users';
import UserProfile from './components/UserProfile/UserProfile';
import Login from './components/Login';
import Signup from './components/Signup';
import NewPost from './components/NewPost/NewPost';

/**
 * App — root component.
 * Sets up BrowserRouter for client-side navigation, wraps the tree
 * in AuthProvider for global auth state, and defines all page routes.
 */
function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <TopBar />
        <Routes>
          <Route path="/" element={<Feed />} />
          <Route path="/users" element={<Users />} />
          <Route path="/profile/:userId" element={<UserProfile />} />
          <Route path="/user-posts/:userId" element={<Feed />} />
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          <Route path="/new-post" element={<NewPost />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
