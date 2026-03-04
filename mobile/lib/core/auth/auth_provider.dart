import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:agentic_app/core/storage/token_storage.dart';

/// Simple auth state: authenticated or not.
class AuthState {
  final bool isAuthenticated;
  final String? userId;
  final String? email;

  const AuthState({
    this.isAuthenticated = false,
    this.userId,
    this.email,
  });

  AuthState copyWith({
    bool? isAuthenticated,
    String? userId,
    String? email,
  }) {
    return AuthState(
      isAuthenticated: isAuthenticated ?? this.isAuthenticated,
      userId: userId ?? this.userId,
      email: email ?? this.email,
    );
  }
}

/// Manages authentication state globally.
class AuthNotifier extends StateNotifier<AuthState> {
  final TokenStorage _tokenStorage;

  AuthNotifier(this._tokenStorage) : super(const AuthState()) {
    _init();
  }

  Future<void> _init() async {
    final token = await _tokenStorage.getAccessToken();
    if (token != null) {
      state = state.copyWith(isAuthenticated: true);
    }
  }

  Future<void> login({
    required String accessToken,
    required String refreshToken,
    String? userId,
    String? email,
  }) async {
    await _tokenStorage.saveTokens(
      access: accessToken,
      refresh: refreshToken,
    );
    state = AuthState(
      isAuthenticated: true,
      userId: userId,
      email: email,
    );
  }

  Future<void> logout() async {
    await _tokenStorage.clearTokens();
    state = const AuthState();
  }
}

final authStateProvider =
    StateNotifierProvider<AuthNotifier, AuthState>((ref) {
  final storage = ref.watch(tokenStorageProvider);
  return AuthNotifier(storage);
});
