import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:agentic_app/core/auth/auth_provider.dart';

/// Settings screen — user profile, linked accounts, preferences.
class SettingsScreen extends ConsumerWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final auth = ref.watch(authStateProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Settings')),
      body: ListView(
        children: [
          // ── Profile section ──────────────────────
          const _SectionHeader(title: 'Account'),
          ListTile(
            leading: const CircleAvatar(child: Icon(Icons.person)),
            title: Text(auth.email ?? 'User'),
            subtitle: const Text('Edit profile'),
            trailing: const Icon(Icons.chevron_right),
            onTap: () {/* TODO: profile editor */},
          ),

          // ── Linked Accounts ─────────────────────
          const _SectionHeader(title: 'Linked Accounts'),
          ListTile(
            leading: const Icon(Icons.mail),
            title: const Text('Gmail'),
            subtitle: const Text('Not connected'),
            trailing: OutlinedButton(
              onPressed: () {/* TODO: OAuth flow */},
              child: const Text('Connect'),
            ),
          ),
          ListTile(
            leading: const Icon(Icons.mail_outline),
            title: const Text('Outlook'),
            subtitle: const Text('Not connected'),
            trailing: OutlinedButton(
              onPressed: () {/* TODO: OAuth flow */},
              child: const Text('Connect'),
            ),
          ),
          ListTile(
            leading: const Icon(Icons.calendar_month),
            title: const Text('Google Calendar'),
            subtitle: const Text('Not connected'),
            trailing: OutlinedButton(
              onPressed: () {/* TODO: OAuth flow */},
              child: const Text('Connect'),
            ),
          ),

          // ── Preferences ─────────────────────────
          const _SectionHeader(title: 'Preferences'),
          SwitchListTile(
            title: const Text('Push notifications'),
            subtitle: const Text('Get notified for new actions'),
            value: true,
            onChanged: (_) {/* TODO */},
          ),
          ListTile(
            leading: const Icon(Icons.history),
            title: const Text('Audit Log'),
            trailing: const Icon(Icons.chevron_right),
            onTap: () {/* TODO: navigate to audit */},
          ),

          // ── Logout ──────────────────────────────
          const _SectionHeader(title: ''),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: FilledButton.icon(
              onPressed: () async {
                await ref.read(authStateProvider.notifier).logout();
              },
              icon: const Icon(Icons.logout),
              label: const Text('Sign Out'),
              style: FilledButton.styleFrom(
                backgroundColor: Theme.of(context).colorScheme.error,
              ),
            ),
          ),
          const SizedBox(height: 32),
        ],
      ),
    );
  }
}

class _SectionHeader extends StatelessWidget {
  final String title;
  const _SectionHeader({required this.title});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 24, 16, 8),
      child: Text(title,
          style: Theme.of(context).textTheme.labelLarge?.copyWith(
                color: Theme.of(context).colorScheme.primary,
              )),
    );
  }
}
