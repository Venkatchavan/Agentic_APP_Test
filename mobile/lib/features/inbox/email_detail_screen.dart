import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:agentic_app/services/inbox_service.dart';
import 'package:agentic_app/models/email_model.dart';
import 'package:agentic_app/shared/widgets/common_widgets.dart';

/// Email detail — shows body, extracted actions, and draft trigger.
class EmailDetailScreen extends ConsumerStatefulWidget {
  final String emailId;
  const EmailDetailScreen({super.key, required this.emailId});

  @override
  ConsumerState<EmailDetailScreen> createState() => _EmailDetailScreenState();
}

class _EmailDetailScreenState extends ConsumerState<EmailDetailScreen> {
  EmailModel? _email;
  bool _loading = true;
  bool _extracting = false;
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
      _email = await svc.getEmail(widget.emailId);
    } catch (e) {
      _error = 'Failed to load email';
    }
    if (mounted) setState(() => _loading = false);
  }

  Future<void> _extractActions() async {
    setState(() => _extracting = true);
    try {
      final svc = ref.read(inboxServiceProvider);
      final actions = await svc.extractActions(widget.emailId);
      setState(() {
        _email = EmailModel(
          id: _email!.id,
          subject: _email!.subject,
          senderEmail: _email!.senderEmail,
          senderName: _email!.senderName,
          snippet: _email!.snippet,
          receivedAt: _email!.receivedAt,
          isRead: _email!.isRead,
          actions: actions,
        );
      });
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Extraction failed')),
      );
    }
    if (mounted) setState(() => _extracting = false);
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) return const Scaffold(body: LoadingIndicator());
    if (_error != null) {
      return Scaffold(
        appBar: AppBar(),
        body: ErrorDisplay(message: _error!, onRetry: _load),
      );
    }
    final email = _email!;

    return Scaffold(
      appBar: AppBar(title: Text(email.subject)),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Text('From: ${email.senderName} <${email.senderEmail}>',
              style: Theme.of(context).textTheme.bodyMedium),
          const Divider(height: 24),
          Text(email.snippet,
              style: Theme.of(context).textTheme.bodyLarge),
          const SizedBox(height: 24),
          FilledButton.icon(
            onPressed: _extracting ? null : _extractActions,
            icon: _extracting
                ? const SizedBox(width: 18, height: 18,
                    child: CircularProgressIndicator(strokeWidth: 2))
                : const Icon(Icons.bolt),
            label: Text(_extracting ? 'Extracting...' : 'Extract Actions'),
          ),
          if (email.actions.isNotEmpty) ...[
            const SizedBox(height: 24),
            Text('Extracted Actions',
                style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 8),
            ...email.actions.map((a) => Card(
                  child: ListTile(
                    leading: _actionIcon(a.actionType),
                    title: Text(a.summary),
                    subtitle: Text('${a.actionType} • ${a.priority ?? "normal"}'),
                  ),
                )),
          ],
        ],
      ),
    );
  }

  Widget _actionIcon(String type) {
    switch (type) {
      case 'reply': return const Icon(Icons.reply, color: Colors.blue);
      case 'schedule': return const Icon(Icons.calendar_today, color: Colors.teal);
      case 'task': return const Icon(Icons.task_alt, color: Colors.orange);
      case 'forward': return const Icon(Icons.forward, color: Colors.purple);
      default: return const Icon(Icons.circle, color: Colors.grey);
    }
  }
}
