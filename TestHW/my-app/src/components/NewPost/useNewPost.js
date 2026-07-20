import { useState, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useEditor } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import { useAuth } from '../../context/AuthContext';
import { createPost } from '../../services/posts.service';
import { uploadPostImage } from '../../services/upload.service';

/**
 * Custom hook for the NewPost form.
 * Manages title, Tiptap editor, image selection/validation/removal,
 * and form submission (upload image → create post → navigate).
 *
 * @returns {{
 *   title: string,
 *   setTitle: function,
 *   error: string,
 *   loading: boolean,
 *   uploading: boolean,
 *   imagePreview: string,
 *   fileInputRef: React.RefObject,
 *   editor: Object,
 *   user: Object|null,
 *   authLoading: boolean,
 *   handleImageSelect: (e: Event) => void,
 *   removeImage: () => void,
 *   handleSubmit: (e: Event) => Promise<void>,
 * }}
 */
export function useNewPost() {
  const [title, setTitle] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [imageFile, setImageFile] = useState(null);
  const [imagePreview, setImagePreview] = useState('');
  const [uploading, setUploading] = useState(false);
  const { user, loading: authLoading } = useAuth();
  const navigate = useNavigate();
  const fileInputRef = useRef(null);

  const editor = useEditor({
    extensions: [StarterKit],
    content: '',
    editorProps: {
      attributes: {
        class: 'tiptap-editor',
      },
    },
  });

  const handleImageSelect = useCallback((e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate file type
    const allowed = ['image/png', 'image/jpeg', 'image/gif', 'image/webp'];
    if (!allowed.includes(file.type)) {
      setError('Invalid file type. Use PNG, JPG, GIF, or WebP.');
      return;
    }

    // Validate file size (5MB)
    if (file.size > 5 * 1024 * 1024) {
      setError('File too large. Maximum size is 5 MB.');
      return;
    }

    setImageFile(file);
    setImagePreview(URL.createObjectURL(file));
    setError('');
  }, []);

  const removeImage = useCallback(() => {
    if (imagePreview) URL.revokeObjectURL(imagePreview);
    setImageFile(null);
    setImagePreview('');
    if (fileInputRef.current) fileInputRef.current.value = '';
  }, [imagePreview]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    const body = editor?.getHTML() || '';
    const textContent = editor?.getText()?.trim() || '';

    // Validation
    if (!title.trim() || !textContent) {
      setError('Please fill in both the title and content.');
      return;
    }

    setLoading(true);
    try {
      let imageUrl = '';

      // Upload image first if selected
      if (imageFile) {
        setUploading(true);
        const uploadResult = await uploadPostImage(imageFile);
        imageUrl = uploadResult.url;
        setUploading(false);
      }

      await createPost(title, body, imageUrl);
      navigate('/');
    } catch (err) {
      setError(err.message);
      setUploading(false);
    } finally {
      setLoading(false);
    }
  };

  return {
    title,
    setTitle,
    error,
    loading,
    uploading,
    imagePreview,
    fileInputRef,
    editor,
    user,
    authLoading,
    handleImageSelect,
    removeImage,
    handleSubmit,
  };
}
