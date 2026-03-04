import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:agentic_app/core/network/api_client.dart';
import 'package:agentic_app/models/meeting_model.dart';
import 'package:agentic_app/models/app_models.dart';

/// Meetings, Drafts, Scheduling API services.

class MeetingsService {
  final Dio _dio;
  MeetingsService(this._dio);

  Future<List<MeetingModel>> listMeetings({int limit = 20, int offset = 0}) async {
    final resp = await _dio.get('/meetings', queryParameters: {
      'limit': limit, 'offset': offset,
    });
    return (resp.data as List).map((e) => MeetingModel.fromJson(e)).toList();
  }

  Future<MeetingModel> getMeeting(String id) async {
    final resp = await _dio.get('/meetings/$id');
    return MeetingModel.fromJson(resp.data);
  }

  Future<void> processMeeting(String id) async {
    await _dio.post('/meetings/$id/process');
  }
}

class DraftsService {
  final Dio _dio;
  DraftsService(this._dio);

  Future<List<DraftModel>> listDrafts({int limit = 20, int offset = 0}) async {
    final resp = await _dio.get('/drafts', queryParameters: {
      'limit': limit, 'offset': offset,
    });
    return (resp.data as List).map((e) => DraftModel.fromJson(e)).toList();
  }

  Future<DraftModel> getDraft(String id) async {
    final resp = await _dio.get('/drafts/$id');
    return DraftModel.fromJson(resp.data);
  }

  Future<DraftModel> editDraft(String id, String newBody) async {
    final resp = await _dio.put('/drafts/$id', data: {'body': newBody});
    return DraftModel.fromJson(resp.data);
  }
}

class SchedulingService {
  final Dio _dio;
  SchedulingService(this._dio);

  Future<List<ScheduleProposalModel>> listProposals({
    int limit = 20, int offset = 0,
  }) async {
    final resp = await _dio.get('/scheduling/proposals', queryParameters: {
      'limit': limit, 'offset': offset,
    });
    return (resp.data as List)
        .map((e) => ScheduleProposalModel.fromJson(e))
        .toList();
  }
}

class ApprovalsService {
  final Dio _dio;
  ApprovalsService(this._dio);

  Future<List<ApprovalModel>> listPending() async {
    final resp = await _dio.get('/approvals/pending');
    return (resp.data as List).map((e) => ApprovalModel.fromJson(e)).toList();
  }

  Future<ApprovalModel> decide(String id, String decision) async {
    final resp = await _dio.post('/approvals/$id/decide', data: {
      'decision': decision,
    });
    return ApprovalModel.fromJson(resp.data);
  }

  Future<void> execute(String id) async {
    await _dio.post('/execution/$id');
  }
}

class NotificationsService {
  final Dio _dio;
  NotificationsService(this._dio);

  Future<List<NotificationModel>> list({bool unreadOnly = false}) async {
    final resp = await _dio.get('/notifications', queryParameters: {
      'unread_only': unreadOnly,
    });
    return (resp.data as List)
        .map((e) => NotificationModel.fromJson(e))
        .toList();
  }

  Future<int> unreadCount() async {
    final resp = await _dio.get('/notifications/unread-count');
    return resp.data['unread_count'] as int;
  }

  Future<void> markRead(String id) async {
    await _dio.post('/notifications/$id/read');
  }
}

// ── Providers ─────────────────────────────────────────
final meetingsServiceProvider = Provider<MeetingsService>(
  (ref) => MeetingsService(ref.watch(dioProvider)),
);
final draftsServiceProvider = Provider<DraftsService>(
  (ref) => DraftsService(ref.watch(dioProvider)),
);
final schedulingServiceProvider = Provider<SchedulingService>(
  (ref) => SchedulingService(ref.watch(dioProvider)),
);
final approvalsServiceProvider = Provider<ApprovalsService>(
  (ref) => ApprovalsService(ref.watch(dioProvider)),
);
final notificationsServiceProvider = Provider<NotificationsService>(
  (ref) => NotificationsService(ref.watch(dioProvider)),
);
