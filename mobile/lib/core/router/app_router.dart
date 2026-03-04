import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:agentic_app/core/auth/auth_provider.dart';
import 'package:agentic_app/features/auth/login_screen.dart';
import 'package:agentic_app/features/auth/register_screen.dart';
import 'package:agentic_app/features/home/home_screen.dart';
import 'package:agentic_app/features/inbox/inbox_screen.dart';
import 'package:agentic_app/features/inbox/email_detail_screen.dart';
import 'package:agentic_app/features/meetings/meetings_screen.dart';
import 'package:agentic_app/features/meetings/meeting_detail_screen.dart';
import 'package:agentic_app/features/drafts/drafts_screen.dart';
import 'package:agentic_app/features/scheduling/scheduling_screen.dart';
import 'package:agentic_app/features/approvals/approvals_screen.dart';
import 'package:agentic_app/features/settings/settings_screen.dart';
import 'package:agentic_app/features/audit/audit_screen.dart';
import 'package:agentic_app/shared/widgets/shell_scaffold.dart';

final appRouterProvider = Provider<GoRouter>((ref) {
  final authState = ref.watch(authStateProvider);

  return GoRouter(
    initialLocation: '/home',
    redirect: (context, state) {
      final isLoggedIn = authState.isAuthenticated;
      final isAuthRoute = state.matchedLocation.startsWith('/auth');

      if (!isLoggedIn && !isAuthRoute) return '/auth/login';
      if (isLoggedIn && isAuthRoute) return '/home';
      return null;
    },
    routes: [
      // ── Auth routes (no shell) ─────────────────
      GoRoute(
        path: '/auth/login',
        builder: (_, __) => const LoginScreen(),
      ),
      GoRoute(
        path: '/auth/register',
        builder: (_, __) => const RegisterScreen(),
      ),

      // ── Main app shell ─────────────────────────
      ShellRoute(
        builder: (_, state, child) => ShellScaffold(child: child),
        routes: [
          GoRoute(
            path: '/home',
            builder: (_, __) => const HomeScreen(),
          ),
          GoRoute(
            path: '/inbox',
            builder: (_, __) => const InboxScreen(),
            routes: [
              GoRoute(
                path: ':emailId',
                builder: (_, state) => EmailDetailScreen(
                  emailId: state.pathParameters['emailId']!,
                ),
              ),
            ],
          ),
          GoRoute(
            path: '/meetings',
            builder: (_, __) => const MeetingsScreen(),
            routes: [
              GoRoute(
                path: ':meetingId',
                builder: (_, state) => MeetingDetailScreen(
                  meetingId: state.pathParameters['meetingId']!,
                ),
              ),
            ],
          ),
          GoRoute(
            path: '/drafts',
            builder: (_, __) => const DraftsScreen(),
          ),
          GoRoute(
            path: '/scheduling',
            builder: (_, __) => const SchedulingScreen(),
          ),
          GoRoute(
            path: '/approvals',
            builder: (_, __) => const ApprovalsScreen(),
          ),
          GoRoute(
            path: '/settings',
            builder: (_, __) => const SettingsScreen(),
          ),
          GoRoute(
            path: '/audit',
            builder: (_, __) => const AuditScreen(),
          ),
        ],
      ),
    ],
  );
});
