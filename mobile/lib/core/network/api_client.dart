import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:agentic_app/core/constants.dart';
import 'package:agentic_app/core/storage/token_storage.dart';

/// Provides a configured Dio HTTP client with auth interceptor.
final dioProvider = Provider<Dio>((ref) {
  final dio = Dio(BaseOptions(
    baseUrl: AppConstants.apiBaseUrl,
    connectTimeout: AppConstants.apiTimeout,
    receiveTimeout: AppConstants.apiTimeout,
    headers: {'Content-Type': 'application/json'},
  ));

  dio.interceptors.add(AuthInterceptor(ref));
  dio.interceptors.add(LogInterceptor(
    requestBody: true,
    responseBody: true,
    logPrint: (o) {}, // suppress in release
  ));

  return dio;
});

/// Injects Authorization header and handles 401 refresh.
class AuthInterceptor extends Interceptor {
  final Ref _ref;

  AuthInterceptor(this._ref);

  @override
  void onRequest(
    RequestOptions options,
    RequestInterceptorHandler handler,
  ) async {
    final storage = _ref.read(tokenStorageProvider);
    final token = await storage.getAccessToken();
    if (token != null) {
      options.headers['Authorization'] = 'Bearer $token';
    }
    handler.next(options);
  }

  @override
  void onError(
    DioException err,
    ErrorInterceptorHandler handler,
  ) async {
    if (err.response?.statusCode == 401) {
      final refreshed = await _tryRefresh();
      if (refreshed) {
        // Retry original request with new token
        final storage = _ref.read(tokenStorageProvider);
        final newToken = await storage.getAccessToken();
        err.requestOptions.headers['Authorization'] = 'Bearer $newToken';
        try {
          final response = await Dio().fetch(err.requestOptions);
          return handler.resolve(response);
        } catch (e) {
          return handler.next(err);
        }
      }
    }
    handler.next(err);
  }

  Future<bool> _tryRefresh() async {
    try {
      final storage = _ref.read(tokenStorageProvider);
      final refreshToken = await storage.getRefreshToken();
      if (refreshToken == null) return false;

      final resp = await Dio().post(
        '${AppConstants.apiBaseUrl}/auth/refresh',
        data: {'refresh_token': refreshToken},
      );

      if (resp.statusCode == 200) {
        await storage.saveTokens(
          access: resp.data['access_token'],
          refresh: resp.data['refresh_token'],
        );
        return true;
      }
    } catch (_) {}
    return false;
  }
}
