/**
 * Barrel file — re-exports all service functions for convenience.
 * Consumers can import from '@/services' or use specific service files.
 */
export { signupUser, loginUser, logoutUser, fetchCurrentUser } from './auth.service';
export { createComment, fetchComments } from './comments.service';
export { fetchPosts, fetchUserPosts, fetchFollowingPosts, createPost } from './posts.service';
export { toggleLike, fetchPostLikes } from './likes.service';
export { fetchUsers, fetchUser } from './users.service';
export { followUser, unfollowUser, fetchFollowers, fetchFollowing, checkIsFollowing } from './follows.service';
export { updateProfile, uploadProfilePicture } from './profile.service';
export { requestPasswordReset, confirmPasswordReset } from './reset.service';
export { uploadPostImage, uploadPostVideo } from './upload.service';
export { reportPost } from './reports.service';
export { autocorrectText, suggestPost, suggestComment } from './ai.service';
export {
  fetchReports, updateReport, deletePostAsAdmin, fetchAdminUsers, setUserBanned, setUserRole,
} from './admin.service';

