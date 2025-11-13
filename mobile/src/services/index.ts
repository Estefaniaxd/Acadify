/**
 * Services Barrel Export
 * Central point for all service imports
 * 
 * @module services
 */

// Auth Service
export { authService } from './auth.service';
export type {
  LoginRequest,
  LoginResponse,
  OTPRequiredResponse,
  RegisterRequest,
  RegisterResponse,
  RecoverPasswordRequest,
  RecoverPasswordResponse,
  ResetPasswordRequest,
  ResetPasswordResponse,
  RefreshTokenResponse,
} from './auth.service';

// User Service
export { userService } from './user.service';
export type {
  UserProfile,
  UpdateProfileRequest,
  ChangePasswordRequest,
  UploadAvatarResponse,
  UserStatistics,
  UserPreferences,
} from './user.service';

// Course Service
export { courseService } from './course.service';
export type {
  Course,
  CourseWithProgress,
  Lesson,
  LessonWithProgress,
  EnrollCourseRequest,
  EnrollCourseResponse,
  MarkLessonCompleteRequest,
  CourseFilters,
  PaginatedResponse,
  CourseReview,
  AddReviewRequest,
} from './course.service';

// Message Service
export { messageService } from './message.service';
export type {
  Conversation,
  ConversationParticipant,
  Message,
  SendMessageRequest,
  CreateConversationRequest,
  UpdateConversationRequest,
  TypingIndicator,
  PaginatedMessages,
} from './message.service';
