/**
 * Custom Hooks Barrel Export
 * Central point for all custom hooks
 * 
 * @module hooks
 */

// Course Hooks
export {
  useCourses,
  useCourseDetail,
  useEnrolledCourses,
  useCourseLessons,
  useLessonDetail,
  useCourseReviews,
  useCourseCategories,
  useEnrollCourse,
  useMarkLessonComplete,
  useUpdateLessonProgress,
  useAddCourseReview,
  useUnenrollCourse,
  QUERY_KEYS,
} from './useCourses';

// Message Hooks
export {
  useConversations,
  useConversationDetail,
  useConversationMessages,
  useUnreadMessagesCount,
  useCreateConversation,
  useSendMessage,
  useSendFile,
  useEditMessage,
  useDeleteMessage,
  useMarkMessagesAsRead,
  useAddParticipant,
  useRemoveParticipant,
  useLeaveConversation,
  MESSAGE_QUERY_KEYS,
} from './useMessages';

// User Hooks
export {
  useUserProfile,
  useUserById,
  useUserStatistics,
  useUserPreferences,
  useUpdateProfile,
  useChangePassword,
  useUploadAvatar,
  useDeleteAvatar,
  useUpdatePreferences,
  useDeleteAccount,
  USER_QUERY_KEYS,
} from './useUser';

// Auth Hook (re-export from context)
export { useAuth } from '@/context/AuthContext';
