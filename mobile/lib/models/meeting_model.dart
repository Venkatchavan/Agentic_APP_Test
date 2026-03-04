/// Meeting-related data models.

class MeetingModel {
  final String id;
  final String title;
  final String? source;
  final DateTime importedAt;
  final MeetingSummaryModel? summary;

  const MeetingModel({
    required this.id,
    required this.title,
    this.source,
    required this.importedAt,
    this.summary,
  });

  factory MeetingModel.fromJson(Map<String, dynamic> json) => MeetingModel(
        id: json['id'] as String,
        title: json['title'] as String,
        source: json['source'] as String?,
        importedAt: DateTime.parse(json['imported_at'] as String),
        summary: json['summary'] != null
            ? MeetingSummaryModel.fromJson(json['summary'])
            : null,
      );
}

class MeetingSummaryModel {
  final String id;
  final String summaryText;
  final List<MeetingDecisionModel> decisions;
  final List<MeetingActionModel> actionItems;

  const MeetingSummaryModel({
    required this.id,
    required this.summaryText,
    this.decisions = const [],
    this.actionItems = const [],
  });

  factory MeetingSummaryModel.fromJson(Map<String, dynamic> json) =>
      MeetingSummaryModel(
        id: json['id'] as String,
        summaryText: json['summary_text'] as String,
        decisions: (json['decisions'] as List<dynamic>?)
                ?.map((e) => MeetingDecisionModel.fromJson(e))
                .toList() ??
            [],
        actionItems: (json['action_items'] as List<dynamic>?)
                ?.map((e) => MeetingActionModel.fromJson(e))
                .toList() ??
            [],
      );
}

class MeetingDecisionModel {
  final String id;
  final String description;

  const MeetingDecisionModel({required this.id, required this.description});

  factory MeetingDecisionModel.fromJson(Map<String, dynamic> json) =>
      MeetingDecisionModel(
        id: json['id'] as String,
        description: json['description'] as String,
      );
}

class MeetingActionModel {
  final String id;
  final String description;
  final String? assignee;
  final String? dueDate;

  const MeetingActionModel({
    required this.id,
    required this.description,
    this.assignee,
    this.dueDate,
  });

  factory MeetingActionModel.fromJson(Map<String, dynamic> json) =>
      MeetingActionModel(
        id: json['id'] as String,
        description: json['description'] as String,
        assignee: json['assignee'] as String?,
        dueDate: json['due_date'] as String?,
      );
}
