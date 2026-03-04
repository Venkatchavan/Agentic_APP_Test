import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:agentic_app/services/app_services.dart';
import 'package:agentic_app/models/meeting_model.dart';
import 'package:agentic_app/shared/widgets/common_widgets.dart';
import 'package:intl/intl.dart';

/// List of imported meeting transcripts.
class MeetingsScreen extends ConsumerStatefulWidget {
  const MeetingsScreen({super.key});

  @override
  ConsumerState<MeetingsScreen> createState() => _MeetingsScreenState();
}

class _MeetingsScreenState extends ConsumerState<MeetingsScreen> {
  List<MeetingModel> _meetings = [];
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
      _meetings = await ref.read(meetingsServiceProvider).listMeetings();
    } catch (e) {
      _error = 'Failed to load meetings';
    }
    if (mounted) setState(() => _loading = false);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Meetings')),
      body: _loading
          ? const LoadingIndicator(message: 'Loading meetings...')
          : _error != null
              ? ErrorDisplay(message: _error!, onRetry: _load)
              : _meetings.isEmpty
                  ? const EmptyState(
                      icon: Icons.groups,
                      title: 'No meetings yet',
                      subtitle: 'Import a transcript to get started',
                    )
                  : RefreshIndicator(
                      onRefresh: _load,
                      child: ListView.builder(
                        itemCount: _meetings.length,
                        itemBuilder: (_, i) {
                          final m = _meetings[i];
                          final date = DateFormat.yMMMd().format(m.importedAt);
                          return ListTile(
                            leading: CircleAvatar(
                              child: Icon(
                                m.summary != null
                                    ? Icons.check_circle
                                    : Icons.pending,
                              ),
                            ),
                            title: Text(m.title, maxLines: 1,
                                overflow: TextOverflow.ellipsis),
                            subtitle: Text(date),
                            trailing: const Icon(Icons.chevron_right),
                            onTap: () => context.go('/meetings/${m.id}'),
                          );
                        },
                      ),
                    ),
    );
  }
}
