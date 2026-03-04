/// App-wide constants.
class AppConstants {
  AppConstants._();

  static const String appName = 'Agentic';
  static const String apiBaseUrl = 'http://10.0.2.2:8000/api/v1';
  // 10.0.2.2 is Android emulator -> host loopback

  static const Duration apiTimeout = Duration(seconds: 30);
  static const Duration tokenRefreshBuffer = Duration(minutes: 2);

  // Storage keys
  static const String accessTokenKey = 'access_token';
  static const String refreshTokenKey = 'refresh_token';
  static const String userKey = 'current_user';

  // Pagination
  static const int defaultPageSize = 20;
}
