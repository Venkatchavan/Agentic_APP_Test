import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:agentic_app/services/app_services.dart';
import 'package:agentic_app/models/app_models.dart';
import 'package:agentic_app/shared/widgets/common_widgets.dart';

/// Approvals screen — the gatekeeper. No action executes without user consent.
class ApprovalsScreen extends ConsumerStatefulWidget {
  const ApprovalsScreen({super.key});

  @override
  ConsumerState<ApprovalsScreen> createState() => _ApprovalsScreenState();
}

class _ApprovalsScreenState extends ConsumerState<ApprovalsScreen> {
  List<ApprovalModel> _pending = [];
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
      _pending = await ref.read(approvalsServiceProvider).listPending();
    } catch (e) {
      _error = 'Failed to load approvals';
    }
    if (mounted) setState(() => _loading = false);
  }

  Future<void> _decide(String id, String decision) async {
    try {
      await ref.read(approvalsServiceProvider).decide(id, decision);
      if (decision == 'approved') {
        await ref.read(approvalsServiceProvider).execute(id);
      }
      await _load();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Action $decision')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Operation failed')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Approvals')),
      body: _loading
          ? const LoadingIndicator(message: 'Loading approvals...')
          : _error != null
              ? ErrorDisplay(message: _error!, onRetry: _load)
              : _pending.isEmpty
                  ? const EmptyState(
                      icon: Icons.check_circle,
                      title: 'All clear!',
                      subtitle: 'No pending approvals',
                    )
                  : RefreshIndicator(
                      onRefresh: _load,
                      child: ListView.builder(
                        padding: const EdgeInsets.all(16),
                        itemCount: _pending.length,
                        itemBuilder: (_, i) => _ApprovalCard(
                          approval: _pending[i],
                          onDecide: _decide,
                        ),
                      ),
                    ),
    );
  }
}

class _ApprovalCard extends StatelessWidget {
  final ApprovalModel approval;
  final Future<void> Function(String id, String decision) onDecide;

  const _ApprovalCard({required this.approval, required this.onDecide});

  IconData _iconFor(String type) {
    switch (type) {
      case 'send_email': return Icons.send;
      case 'create_calendar_event': return Icons.event;
      case 'send_followup': return Icons.forward_to_inbox;
      default: return Icons.pending_actions;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(_iconFor(approval.actionType), size: 28),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(approval.actionType.replaceAll('_', ' ').toUpperCase(),
                          style: Theme.of(context).textTheme.labelLarge),
                      if (approval.previewSummary != null)
                        Text(approval.previewSummary!,
                            style: Theme.of(context).textTheme.bodyMedium),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                OutlinedButton.icon(
                  onPressed: () => onDecide(approval.id, 'rejected'),
                  icon: const Icon(Icons.close),
                  label: const Text('Reject'),
                  style: OutlinedButton.styleFrom(
                    foregroundColor: Theme.of(context).colorScheme.error,
                  ),
                ),
                const SizedBox(width: 12),
                FilledButton.icon(
                  onPressed: () => onDecide(approval.id, 'approved'),
                  icon: const Icon(Icons.check),
                  label: const Text('Approve'),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
