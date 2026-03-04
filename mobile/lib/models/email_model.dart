/// Data models for the API layer.
/// All models use manual fromJson/toJson for simplicity.

class UserModel {
  final String id;
  final String email;
  final String fullName;
  final DateTime createdAt;

  const UserModel({
    required this.id,
    required this.email,
    required this.fullName,
    required this.createdAt,
  });

  factory UserModel.fromJson(Map<String, dynamic> json) => UserModel(
        id: json['id'] as String,
        email: json['email'] as String,
        fullName: json['full_name'] as String,
        createdAt: DateTime.parse(json['created_at'] as String),
      );
}

class EmailModel {
  final String id;
  final String subject;
  final String senderEmail;
  final String senderName;
  final String snippet;
  final DateTime receivedAt;
  final bool isRead;
  final List<EmailAction> actions;

  const EmailModel({
    required this.id,
    required this.subject,
    required this.senderEmail,
    required this.senderName,
    required this.snippet,
    required this.receivedAt,
    this.isRead = false,
    this.actions = const [],
  });

  factory EmailModel.fromJson(Map<String, dynamic> json) => EmailModel(
        id: json['id'] as String,
        subject: json['subject'] as String? ?? '(no subject)',
        senderEmail: json['sender_email'] as String,
        senderName: json['sender_name'] as String? ?? '',
        snippet: json['snippet'] as String? ?? '',
        receivedAt: DateTime.parse(json['received_at'] as String),
        isRead: json['is_read'] as bool? ?? false,
        actions: (json['actions'] as List<dynamic>?)
                ?.map((e) => EmailAction.fromJson(e))
                .toList() ??
            [],
      );
}

class EmailAction {
  final String id;
  final String actionType;
  final String summary;
  final String? priority;
  final String? dueDate;

  const EmailAction({
    required this.id,
    required this.actionType,
    required this.summary,
    this.priority,
    this.dueDate,
  });

  factory EmailAction.fromJson(Map<String, dynamic> json) => EmailAction(
        id: json['id'] as String,
        actionType: json['action_type'] as String,
        summary: json['summary'] as String,
        priority: json['priority'] as String?,
        dueDate: json['due_date'] as String?,
      );
}
