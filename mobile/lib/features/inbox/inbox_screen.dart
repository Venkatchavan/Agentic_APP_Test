import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:agentic_app/services/inbox_service.dart';
import 'package:agentic_app/models/email_model.dart';
import 'package:agentic_app/shared/widgets/common_widgets.dart';
import 'package:intl/intl.dart';

/// Inbox list — shows ingested emails with extracted actions.
class InboxScreen extends ConsumerStatefulWidget {
  const InboxScreen({super.key});

  @override
  ConsumerState<InboxScreen> createState() => _InboxScreenState();
}

class _InboxScreenState extends ConsumerState<InboxScreen> {
  List<EmailModel> _emails = [];
  bool _loading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() { _loading = true; _error = null; });
    try {
      final svc = ref.read(inboxServiceProvider);
      _emails = await svc.listEmails();
    } catch (e) {
      _error = 'Failed to load emails';
    }
    if (mounted) setState(() => _loading = false);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Inbox')),
      body: _loading
          ? const LoadingIndicator(message: 'Loading emails...')
          : _error != null
              ? ErrorDisplay(message: _error!, onRetry: _load)
              : _emails.isEmpty
                  ? const EmptyState(
                      icon: Icons.inbox,
                      title: 'No emails yet',
                      subtitle: 'Link an account to start ingesting',
                    )
                  : RefreshIndicator(
                      onRefresh: _load,
                      child: ListView.builder(
                        itemCount: _emails.length,
                        itemBuilder: (_, i) => _EmailTile(
                          email: _emails[i],
                          onTap: () =>
                              context.go('/inbox/${_emails[i].id}'),
                        ),
                      ),
                    ),
    );
  }
}

class _EmailTile extends StatelessWidget {
  final EmailModel email;
  final VoidCallback onTap;
  const _EmailTile({required this.email, required this.onTap});

  @override
  Widget build(BuildContext context) {
    final time = DateFormat.MMMd().add_jm().format(email.receivedAt);
    final hasActions = email.actions.isNotEmpty;

    return ListTile(
      leading: CircleAvatar(
        child: Text(email.senderName.isNotEmpty
            ? email.senderName[0].toUpperCase()
            : '?'),
      ),
      title: Text(email.subject,
          maxLines: 1, overflow: TextOverflow.ellipsis,
          style: TextStyle(
            fontWeight: email.isRead ? FontWeight.normal : FontWeight.bold,
          )),
      subtitle: Text('${email.senderName} • $time',
          maxLines: 1, overflow: TextOverflow.ellipsis),
      trailing: hasActions
          ? Badge(label: Text('${email.actions.length}'),
              child: const Icon(Icons.bolt))
          : null,
      onTap: onTap,
    );
  }
}
