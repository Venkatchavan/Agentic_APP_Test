import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:agentic_app/services/app_services.dart';
import 'package:agentic_app/models/app_models.dart';
import 'package:agentic_app/shared/widgets/common_widgets.dart';

/// Scheduling screen — view AI-proposed calendar slots.
class SchedulingScreen extends ConsumerStatefulWidget {
  const SchedulingScreen({super.key});

  @override
  ConsumerState<SchedulingScreen> createState() => _SchedulingScreenState();
}

class _SchedulingScreenState extends ConsumerState<SchedulingScreen> {
  List<ScheduleProposalModel> _proposals = [];
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
      _proposals =
          await ref.read(schedulingServiceProvider).listProposals();
    } catch (e) {
      _error = 'Failed to load proposals';
    }
    if (mounted) setState(() => _loading = false);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Scheduling')),
      body: _loading
          ? const LoadingIndicator(message: 'Loading proposals...')
          : _error != null
              ? ErrorDisplay(message: _error!, onRetry: _load)
              : _proposals.isEmpty
                  ? const EmptyState(
                      icon: Icons.calendar_month,
                      title: 'No proposals yet',
                      subtitle: 'AI will suggest slots based on actions',
                    )
                  : RefreshIndicator(
                      onRefresh: _load,
                      child: ListView.builder(
                        itemCount: _proposals.length,
                        itemBuilder: (_, i) {
                          final p = _proposals[i];
                          return Card(
                            margin: const EdgeInsets.symmetric(
                                horizontal: 16, vertical: 6),
                            child: ListTile(
                              leading: const Icon(Icons.event),
                              title: Text(p.title),
                              subtitle: Text(
                                '${p.proposedStart} - ${p.proposedEnd}'),
                              trailing: Chip(
                                label: Text(p.status),
                                backgroundColor: p.status == 'proposed'
                                    ? Colors.amber.shade100
                                    : Colors.green.shade100,
                              ),
                            ),
                          );
                        },
                      ),
                    ),
    );
  }
}
