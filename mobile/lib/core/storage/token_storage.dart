import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:agentic_app/core/constants.dart';

/// Provides secure token storage.
final secureStorageProvider = Provider<FlutterSecureStorage>(
  (_) => const FlutterSecureStorage(),
);

/// Service for storing / retrieving auth tokens securely.
class TokenStorage {
  final FlutterSecureStorage _storage;

  TokenStorage(this._storage);

  Future<void> saveTokens({
    required String access,
    required String refresh,
  }) async {
    await _storage.write(
        key: AppConstants.accessTokenKey, value: access);
    await _storage.write(
        key: AppConstants.refreshTokenKey, value: refresh);
  }

  Future<String?> getAccessToken() =>
      _storage.read(key: AppConstants.accessTokenKey);

  Future<String?> getRefreshToken() =>
      _storage.read(key: AppConstants.refreshTokenKey);

  Future<void> clearTokens() async {
    await _storage.delete(key: AppConstants.accessTokenKey);
    await _storage.delete(key: AppConstants.refreshTokenKey);
  }
}

final tokenStorageProvider = Provider<TokenStorage>(
  (ref) => TokenStorage(ref.watch(secureStorageProvider)),
);
