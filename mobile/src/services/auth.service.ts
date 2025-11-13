/**
 * Authentication Service
 * Handles all authentication-related API calls
 * 
 * @module services/auth
 * @implements Repository Pattern
 * @follows Single Responsibility Principle
 */

import { apiClient } from '@/utils/api';
import { AxiosResponse } from 'axios';

// ==================== TYPES ====================

/**
 * Login request payload
 */
export interface LoginRequest {
  identifier: string;
  password: string;
  remember?: boolean;
  otp_code?: string;
}

/**
 * Login response from API
 */
export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in?: number;
}

/**
 * OTP required response
 */
export interface OTPRequiredResponse {
  status: 'otp_required';
  message: string;
  expires_in?: number;
}

/**
 * Register request payload
 */
export interface RegisterRequest {
  username: string;
  nombres: string;
  apellidos: string;
  tipo_documento: string;
  numero_documento: string;
  password: string;
  rol: 'estudiante' | 'docente' | 'admin';
  correo_institucional: string;
}

/**
 * Register response from API
 */
export interface RegisterResponse {
  message: string;
  user_id: string;
  username: string;
  email: string;
}

/**
 * Password recovery request
 */
export interface RecoverPasswordRequest {
  email: string;
}

/**
 * Password recovery response
 */
export interface RecoverPasswordResponse {
  message: string;
  email: string;
}

/**
 * Reset password request
 */
export interface ResetPasswordRequest {
  token: string;
  password: string;
}

/**
 * Reset password response
 */
export interface ResetPasswordResponse {
  message: string;
}

/**
 * Token refresh response
 */
export interface RefreshTokenResponse {
  access_token: string;
  refresh_token?: string;
  token_type: string;
  expires_in?: number;
}

// ==================== SERVICE ====================

/**
 * Authentication Service
 * Provides methods for user authentication operations
 * 
 * @class AuthService
 * @implements Repository Pattern
 */
class AuthService {
  private readonly baseUrl = '/auth';

  /**
   * Login with credentials
   * 
   * @param {LoginRequest} credentials - User credentials
   * @returns {Promise<LoginResponse | OTPRequiredResponse>} Authentication tokens or OTP request
   * @throws {AxiosError} If authentication fails
   * 
   * @example
   * ```typescript
   * const response = await authService.login({
   *   identifier: 'johndoe',
   *   password: 'securePassword123',
   *   remember: true
   * });
   * ```
   */
  async login(credentials: LoginRequest): Promise<LoginResponse | OTPRequiredResponse> {
    const response: AxiosResponse<LoginResponse | OTPRequiredResponse> = await apiClient.post(
      `${this.baseUrl}/login`,
      credentials
    );
    return response.data;
  }

  /**
   * Register new user
   * 
   * @param {RegisterRequest} userData - User registration data
   * @returns {Promise<RegisterResponse>} Registration confirmation
   * @throws {AxiosError} If registration fails
   * 
   * @example
   * ```typescript
   * const response = await authService.register({
   *   username: 'johndoe',
   *   nombres: 'John',
   *   apellidos: 'Doe',
   *   tipo_documento: 'cc',
   *   numero_documento: '1234567890',
   *   password: 'securePassword123',
   *   rol: 'estudiante',
   *   correo_institucional: 'john.doe@acadify.com'
   * });
   * ```
   */
  async register(userData: RegisterRequest): Promise<RegisterResponse> {
    const response: AxiosResponse<RegisterResponse> = await apiClient.post(
      `${this.baseUrl}/register`,
      userData
    );
    return response.data;
  }

  /**
   * Logout current user
   * Invalidates tokens on server-side
   * 
   * @returns {Promise<void>}
   * @throws {AxiosError} If logout fails
   * 
   * @example
   * ```typescript
   * await authService.logout();
   * ```
   */
  async logout(): Promise<void> {
    await apiClient.post(`${this.baseUrl}/logout`);
  }

  /**
   * Refresh access token using refresh token
   * 
   * @returns {Promise<RefreshTokenResponse>} New access token
   * @throws {AxiosError} If token refresh fails
   * 
   * @example
   * ```typescript
   * const response = await authService.refreshToken();
   * ```
   */
  async refreshToken(): Promise<RefreshTokenResponse> {
    const response: AxiosResponse<RefreshTokenResponse> = await apiClient.post(
      `${this.baseUrl}/refresh`
    );
    return response.data;
  }

  /**
   * Request password recovery email
   * 
   * @param {string} email - User email address
   * @returns {Promise<RecoverPasswordResponse>} Recovery email confirmation
   * @throws {AxiosError} If email not found or request fails
   * 
   * @example
   * ```typescript
   * const response = await authService.recoverPassword('john.doe@acadify.com');
   * ```
   */
  async recoverPassword(email: string): Promise<RecoverPasswordResponse> {
    const response: AxiosResponse<RecoverPasswordResponse> = await apiClient.post(
      `${this.baseUrl}/recover`,
      { email }
    );
    return response.data;
  }

  /**
   * Reset password using recovery token
   * 
   * @param {string} token - Password reset token from email
   * @param {string} newPassword - New password
   * @returns {Promise<ResetPasswordResponse>} Password reset confirmation
   * @throws {AxiosError} If token invalid or expired
   * 
   * @example
   * ```typescript
   * const response = await authService.resetPassword(
   *   'reset-token-from-email',
   *   'newSecurePassword123'
   * );
   * ```
   */
  async resetPassword(token: string, newPassword: string): Promise<ResetPasswordResponse> {
    const response: AxiosResponse<ResetPasswordResponse> = await apiClient.post(
      `${this.baseUrl}/reset`,
      { token, password: newPassword }
    );
    return response.data;
  }

  /**
   * Verify OTP code
   * 
   * @param {string} otpCode - OTP code from authenticator app
   * @param {string} identifier - User identifier (username/email)
   * @returns {Promise<LoginResponse>} Authentication tokens
   * @throws {AxiosError} If OTP invalid
   * 
   * @example
   * ```typescript
   * const response = await authService.verifyOTP('123456', 'johndoe');
   * ```
   */
  async verifyOTP(otpCode: string, identifier: string): Promise<LoginResponse> {
    const response: AxiosResponse<LoginResponse> = await apiClient.post(
      `${this.baseUrl}/verify-otp`,
      { otp_code: otpCode, identifier }
    );
    return response.data;
  }

  /**
   * Enable two-factor authentication
   * 
   * @returns {Promise<{qr_code: string; secret: string}>} QR code and secret
   * @throws {AxiosError} If request fails
   */
  async enableTwoFactor(): Promise<{ qr_code: string; secret: string }> {
    const response = await apiClient.post(`${this.baseUrl}/enable-2fa`);
    return response.data;
  }

  /**
   * Disable two-factor authentication
   * 
   * @param {string} password - User password for confirmation
   * @returns {Promise<{message: string}>} Confirmation message
   * @throws {AxiosError} If password incorrect or request fails
   */
  async disableTwoFactor(password: string): Promise<{ message: string }> {
    const response = await apiClient.post(`${this.baseUrl}/disable-2fa`, { password });
    return response.data;
  }
}

// Export singleton instance
export const authService = new AuthService();
export default authService;
