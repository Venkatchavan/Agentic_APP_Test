import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:agentic_app/core/network/api_client.dart';
import 'package:agentic_app/models/email_model.dart';

/// Inbox API service.
class InboxService {
  final Dio _dio;

  InboxService(this._dio);

  Future<List<EmailModel>> listEmails({
    int limit = 20,
    int offset = 0,
  }) async {
    final resp = await _dio.get('/inbox/emails', queryParameters: {
      'limit': limit,
      'offset': offset,
    });
    final list = resp.data as List<dynamic>;
    return list.map((e) => EmailModel.fromJson(e)).toList();
  }

  Future<EmailModel> getEmail(String emailId) async {
    final resp = await _dio.get('/inbox/emails/$emailId');
    return EmailModel.fromJson(resp.data);
  }

  Future<List<EmailAction>> extractActions(String emailId) async {
    final resp = await _dio.post('/inbox/emails/$emailId/extract');
    final list = resp.data['actions'] as List<dynamic>;
    return list.map((e) => EmailAction.fromJson(e)).toList();
  }

  Future<void> ingestEmails(String accountId) async {
    await _dio.post('/inbox/ingest', data: {'account_id': accountId});
  }
}

final inboxServiceProvider = Provider<InboxService>(
  (ref) => InboxService(ref.watch(dioProvider)),
);
