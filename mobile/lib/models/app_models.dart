/// Draft, Approval, and Notification models.

class DraftModel {
  final String id;
  final String draftType;
  final String subject;
  final String body;
  final String status;
  final DateTime createdAt;

  const DraftModel({
    required this.id,
    required this.draftType,
    required this.subject,
    required this.body,
    required this.status,
    required this.createdAt,
  });

  factory DraftModel.fromJson(Map<String, dynamic> json) => DraftModel(
        id: json['id'] as String,
        draftType: json['draft_type'] as String? ?? 'reply',
        subject: json['subject'] as String? ?? '',
        body: json['body'] as String,
        status: json['status'] as String? ?? 'draft',
        createdAt: DateTime.parse(json['created_at'] as String),
      );
}

class ApprovalModel {
  final String id;
  final String actionType;
  final String targetResourceId;
  final String status;
  final String? previewSummary;
  final DateTime createdAt;
  final String? executionResult;

  const ApprovalModel({
    required this.id,
    required this.actionType,
    required this.targetResourceId,
    required this.status,
    this.previewSummary,
    required this.createdAt,
    this.executionResult,
  });

  factory ApprovalModel.fromJson(Map<String, dynamic> json) => ApprovalModel(
        id: json['id'] as String,
        actionType: json['action_type'] as String,
        targetResourceId: json['target_resource_id'] as String,
        status: json['status'] as String,
        previewSummary: json['preview_summary'] as String?,
        createdAt: DateTime.parse(json['created_at'] as String),
        executionResult: json['execution_result'] as String?,
      );
}

class NotificationModel {
  final String id;
  final String title;
  final String body;
  final String notificationType;
  final bool isRead;
  final DateTime createdAt;

  const NotificationModel({
    required this.id,
    required this.title,
    required this.body,
    required this.notificationType,
    required this.isRead,
    required this.createdAt,
  });

  factory NotificationModel.fromJson(Map<String, dynamic> json) =>
      NotificationModel(
        id: json['id'] as String,
        title: json['title'] as String,
        body: json['body'] as String,
        notificationType: json['notification_type'] as String,
        isRead: json['is_read'] as bool? ?? false,
        createdAt: DateTime.parse(json['created_at'] as String),
      );
}

class ScheduleProposalModel {
  final String id;
  final String title;
  final String proposedStart;
  final String proposedEnd;
  final String status;
  final DateTime createdAt;

  const ScheduleProposalModel({
    required this.id,
    required this.title,
    required this.proposedStart,
    required this.proposedEnd,
    required this.status,
    required this.createdAt,
  });

  factory ScheduleProposalModel.fromJson(Map<String, dynamic> json) =>
      ScheduleProposalModel(
        id: json['id'] as String,
        title: json['title'] as String? ?? '',
        proposedStart: json['proposed_start'] as String,
        proposedEnd: json['proposed_end'] as String,
        status: json['status'] as String? ?? 'proposed',
        createdAt: DateTime.parse(json['created_at'] as String),
      );
}

class AuditEventModel {
  final String id;
  final String eventType;
  final String? resourceType;
  final String? detail;
  final DateTime createdAt;

  const AuditEventModel({
    required this.id,
    required this.eventType,
    this.resourceType,
    this.detail,
    required this.createdAt,
  });

  factory AuditEventModel.fromJson(Map<String, dynamic> json) =>
      AuditEventModel(
        id: json['id'] as String,
        eventType: json['event_type'] as String,
        resourceType: json['resource_type'] as String?,
        detail: json['detail'] as String?,
        createdAt: DateTime.parse(json['created_at'] as String),
      );
}
