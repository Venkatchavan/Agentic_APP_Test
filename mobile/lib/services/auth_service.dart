import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:agentic_app/core/network/api_client.dart';

/// Auth API service.
class AuthService {
  final Dio _dio;

  AuthService(this._dio);

  Future<Map<String, dynamic>> register({
    required String email,
    required String password,
    required String fullName,
  }) async {
    final resp = await _dio.post('/auth/register', data: {
      'email': email,
      'password': password,
      'full_name': fullName,
    });
    return resp.data as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> login({
    required String email,
    required String password,
  }) async {
    final resp = await _dio.post('/auth/login', data: {
      'email': email,
      'password': password,
    });
    return resp.data as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> refresh(String refreshToken) async {
    final resp = await _dio.post('/auth/refresh', data: {
      'refresh_token': refreshToken,
    });
    return resp.data as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> getMe() async {
    final resp = await _dio.get('/auth/me');
    return resp.data as Map<String, dynamic>;
  }
}

final authServiceProvider = Provider<AuthService>(
  (ref) => AuthService(ref.watch(dioProvider)),
);
