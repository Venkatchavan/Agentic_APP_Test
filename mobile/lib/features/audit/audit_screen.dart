import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:dio/dio.dart';
import 'package:agentic_app/core/network/api_client.dart';
import 'package:agentic_app/models/app_models.dart';
import 'package:agentic_app/shared/widgets/common_widgets.dart';
import 'package:intl/intl.dart';

/// Audit log screen — immutable event trail.
class AuditScreen extends ConsumerStatefulWidget {
  const AuditScreen({super.key});

  @override
  ConsumerState<AuditScreen> createState() => _AuditScreenState();
}

class _AuditScreenState extends ConsumerState<AuditScreen> {
  List<AuditEventModel> _events = [];
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
      final dio = ref.read(dioProvider);
      final resp = await dio.get('/audit/events', queryParameters: {
        'limit': 50,
      });
      _events = (resp.data as List)
          .map((e) => AuditEventModel.fromJson(e))
          .toList();
    } catch (e) {
      _error = 'Failed to load audit events';
    }
    if (mounted) setState(() => _loading = false);
  }

  IconData _iconFor(String type) {
    if (type.contains('email')) return Icons.email;
    if (type.contains('approval')) return Icons.check_circle;
    if (type.contains('execution')) return Icons.play_circle;
    if (type.contains('auth')) return Icons.lock;
    if (type.contains('draft')) return Icons.edit;
    return Icons.info;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Audit Log')),
      body: _loading
          ? const LoadingIndicator(message: 'Loading audit events...')
          : _error != null
              ? ErrorDisplay(message: _error!, onRetry: _load)
              : _events.isEmpty
                  ? const EmptyState(
                      icon: Icons.history,
                      title: 'No events yet',
                      subtitle: 'Activity will appear here',
                    )
                  : RefreshIndicator(
                      onRefresh: _load,
                      child: ListView.builder(
                        itemCount: _events.length,
                        itemBuilder: (_, i) {
                          final e = _events[i];
                          final time = DateFormat.MMMd()
                              .add_jm()
                              .format(e.createdAt);
                          return ListTile(
                            leading: Icon(_iconFor(e.eventType)),
                            title: Text(e.eventType),
                            subtitle: Text(
                              [
                                if (e.resourceType != null) e.resourceType!,
                                time,
                              ].join(' • '),
                            ),
                            trailing:
                                e.detail != null
                                    ? const Icon(Icons.info_outline)
                                    : null,
                            onTap: e.detail != null
                                ? () => _showDetail(context, e)
                                : null,
                          );
                        },
                      ),
                    ),
    );
  }

  void _showDetail(BuildContext context, AuditEventModel event) {
    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        title: Text(event.eventType),
        content: SingleChildScrollView(
          child: Text(event.detail ?? 'No details'),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Close'),
          ),
        ],
      ),
    );
  }
}
