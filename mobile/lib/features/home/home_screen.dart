import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:agentic_app/services/app_services.dart';
import 'package:agentic_app/models/app_models.dart';

/// Home dashboard — quick stats and pending approvals.
class HomeScreen extends ConsumerStatefulWidget {
  const HomeScreen({super.key});

  @override
  ConsumerState<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends ConsumerState<HomeScreen> {
  int _unreadNotifications = 0;
  int _pendingApprovals = 0;
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _loadDashboard();
  }

  Future<void> _loadDashboard() async {
    try {
      final notifService = ref.read(notificationsServiceProvider);
      final approvalService = ref.read(approvalsServiceProvider);

      final results = await Future.wait([
        notifService.unreadCount(),
        approvalService.listPending(),
      ]);

      if (mounted) {
        setState(() {
          _unreadNotifications = results[0] as int;
          _pendingApprovals = (results[1] as List).length;
          _loading = false;
        });
      }
    } catch (_) {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Agentic'),
        actions: [
          IconButton(
            icon: Badge(
              isLabelVisible: _unreadNotifications > 0,
              label: Text('$_unreadNotifications'),
              child: const Icon(Icons.notifications_outlined),
            ),
            onPressed: () {/* TODO: notifications sheet */},
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _loadDashboard,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            Text('Dashboard',
                style: Theme.of(context).textTheme.headlineSmall),
            const SizedBox(height: 16),
            _DashCard(
              icon: Icons.inbox, color: cs.primary,
              title: 'Inbox', subtitle: 'Review extracted actions',
              onTap: () => context.go('/inbox'),
            ),
            _DashCard(
              icon: Icons.groups, color: cs.secondary,
              title: 'Meetings', subtitle: 'AI-processed transcripts',
              onTap: () => context.go('/meetings'),
            ),
            _DashCard(
              icon: Icons.edit_note, color: cs.tertiary,
              title: 'Drafts', subtitle: 'Review & send AI drafts',
              onTap: () => context.go('/drafts'),
            ),
            _DashCard(
              icon: Icons.check_circle_outline, color: cs.error,
              title: 'Approvals',
              subtitle: '$_pendingApprovals pending',
              onTap: () => context.go('/approvals'),
            ),
            _DashCard(
              icon: Icons.calendar_month, color: Colors.teal,
              title: 'Scheduling', subtitle: 'Calendar proposals',
              onTap: () => context.go('/scheduling'),
            ),
          ],
        ),
      ),
    );
  }
}

class _DashCard extends StatelessWidget {
  final IconData icon;
  final Color color;
  final String title;
  final String subtitle;
  final VoidCallback onTap;

  const _DashCard({
    required this.icon, required this.color,
    required this.title, required this.subtitle,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: color.withOpacity(0.12),
          child: Icon(icon, color: color),
        ),
        title: Text(title),
        subtitle: Text(subtitle),
        trailing: const Icon(Icons.chevron_right),
        onTap: onTap,
      ),
    );
  }
}
