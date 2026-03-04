import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:agentic_app/services/app_services.dart';
import 'package:agentic_app/models/app_models.dart';
import 'package:agentic_app/shared/widgets/common_widgets.dart';
import 'package:intl/intl.dart';

/// Drafts list — AI-generated replies and follow-ups.
class DraftsScreen extends ConsumerStatefulWidget {
  const DraftsScreen({super.key});

  @override
  ConsumerState<DraftsScreen> createState() => _DraftsScreenState();
}

class _DraftsScreenState extends ConsumerState<DraftsScreen> {
  List<DraftModel> _drafts = [];
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
      _drafts = await ref.read(draftsServiceProvider).listDrafts();
    } catch (e) {
      _error = 'Failed to load drafts';
    }
    if (mounted) setState(() => _loading = false);
  }

  void _openDraft(DraftModel draft) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      builder: (_) => _DraftEditor(draft: draft, onSaved: _load),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Drafts')),
      body: _loading
          ? const LoadingIndicator(message: 'Loading drafts...')
          : _error != null
              ? ErrorDisplay(message: _error!, onRetry: _load)
              : _drafts.isEmpty
                  ? const EmptyState(
                      icon: Icons.edit_note,
                      title: 'No drafts',
                      subtitle: 'Drafts will appear after action extraction',
                    )
                  : RefreshIndicator(
                      onRefresh: _load,
                      child: ListView.builder(
                        itemCount: _drafts.length,
                        itemBuilder: (_, i) {
                          final d = _drafts[i];
                          return ListTile(
                            leading: Icon(
                              d.draftType == 'reply'
                                  ? Icons.reply
                                  : Icons.forward_to_inbox,
                            ),
                            title: Text(d.subject, maxLines: 1,
                                overflow: TextOverflow.ellipsis),
                            subtitle: Text(
                              '${d.draftType} • ${d.status}'),
                            trailing: const Icon(Icons.edit),
                            onTap: () => _openDraft(d),
                          );
                        },
                      ),
                    ),
    );
  }
}

class _DraftEditor extends ConsumerStatefulWidget {
  final DraftModel draft;
  final VoidCallback onSaved;
  const _DraftEditor({required this.draft, required this.onSaved});

  @override
  ConsumerState<_DraftEditor> createState() => _DraftEditorState();
}

class _DraftEditorState extends ConsumerState<_DraftEditor> {
  late final TextEditingController _ctrl;
  bool _saving = false;

  @override
  void initState() {
    super.initState();
    _ctrl = TextEditingController(text: widget.draft.body);
  }

  @override
  void dispose() {
    _ctrl.dispose();
    super.dispose();
  }

  Future<void> _save() async {
    setState(() => _saving = true);
    try {
      await ref.read(draftsServiceProvider).editDraft(
        widget.draft.id, _ctrl.text,
      );
      widget.onSaved();
      Navigator.of(context).pop();
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Save failed')),
      );
    }
    if (mounted) setState(() => _saving = false);
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: EdgeInsets.only(
        bottom: MediaQuery.of(context).viewInsets.bottom,
        left: 16, right: 16, top: 16,
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(widget.draft.subject,
              style: Theme.of(context).textTheme.titleMedium),
          const SizedBox(height: 12),
          TextField(
            controller: _ctrl,
            maxLines: 8,
            decoration: const InputDecoration(
              hintText: 'Edit draft body...',
            ),
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(
                child: OutlinedButton(
                  onPressed: () => Navigator.of(context).pop(),
                  child: const Text('Cancel'),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: FilledButton(
                  onPressed: _saving ? null : _save,
                  child: _saving
                      ? const SizedBox(width: 18, height: 18,
                          child: CircularProgressIndicator(strokeWidth: 2))
                      : const Text('Save'),
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
        ],
      ),
    );
  }
}
