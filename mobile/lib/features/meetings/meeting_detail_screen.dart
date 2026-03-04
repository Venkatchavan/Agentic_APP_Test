import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:agentic_app/services/app_services.dart';
import 'package:agentic_app/models/meeting_model.dart';
import 'package:agentic_app/shared/widgets/common_widgets.dart';

/// Meeting detail — shows summary, decisions, action items.
class MeetingDetailScreen extends ConsumerStatefulWidget {
  final String meetingId;
  const MeetingDetailScreen({super.key, required this.meetingId});

  @override
  ConsumerState<MeetingDetailScreen> createState() =>
      _MeetingDetailScreenState();
}

class _MeetingDetailScreenState extends ConsumerState<MeetingDetailScreen> {
  MeetingModel? _meeting;
  bool _loading = true;
  bool _processing = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() { _loading = true; _error = null; });
    try {
      _meeting = await ref.read(meetingsServiceProvider)
          .getMeeting(widget.meetingId);
    } catch (e) {
      _error = 'Failed to load meeting';
    }
    if (mounted) setState(() => _loading = false);
  }

  Future<void> _process() async {
    setState(() => _processing = true);
    try {
      await ref.read(meetingsServiceProvider).processMeeting(widget.meetingId);
      await _load();
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Processing failed')),
      );
    }
    if (mounted) setState(() => _processing = false);
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
    final m = _meeting!;
    final summary = m.summary;

    return Scaffold(
      appBar: AppBar(title: Text(m.title)),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          if (summary == null) ...[
            const Card(
              child: Padding(
                padding: EdgeInsets.all(16),
                child: Text('This transcript has not been processed yet.'),
              ),
            ),
            const SizedBox(height: 16),
            FilledButton.icon(
              onPressed: _processing ? null : _process,
              icon: _processing
                  ? const SizedBox(width: 18, height: 18,
                      child: CircularProgressIndicator(strokeWidth: 2))
                  : const Icon(Icons.auto_awesome),
              label: Text(_processing ? 'Processing...' : 'Process with AI'),
            ),
          ] else ...[
            Text('Summary', style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 8),
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Text(summary.summaryText),
              ),
            ),
            if (summary.decisions.isNotEmpty) ...[
              const SizedBox(height: 16),
              Text('Decisions', style: Theme.of(context).textTheme.titleMedium),
              ...summary.decisions.map((d) => ListTile(
                    leading: const Icon(Icons.gavel),
                    title: Text(d.description),
                  )),
            ],
            if (summary.actionItems.isNotEmpty) ...[
              const SizedBox(height: 16),
              Text('Action Items',
                  style: Theme.of(context).textTheme.titleMedium),
              ...summary.actionItems.map((a) => ListTile(
                    leading: const Icon(Icons.task_alt),
                    title: Text(a.description),
                    subtitle: Text(
                      [if (a.assignee != null) a.assignee!,
                       if (a.dueDate != null) 'Due: ${a.dueDate}']
                          .join(' • '),
                    ),
                  )),
            ],
          ],
        ],
      ),
    );
  }
}
