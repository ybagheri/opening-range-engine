# Data Quality Report

Symbol: US30
Bars: 50000
Range (UTC): 2026-08-14T01:02:00+00:00 .. 2026-10-05T13:15:00+00:00
Errors: 0  Warnings: 79
Verdict: PASS

## Gap severity model

- ERROR: gap inside a signal window (OR 09:30-09:45 NY or trade 09:45-11:30 NY), or trade window incomplete on a fully-covered day.
- WARNING: gap outside signal windows (disclosed; overnight bars feed EMA lookbacks but never the signal windows), or a partial final day.
- INFO: recurring scheduled daily broker break (same clock-time pattern on >= 3 distinct NY days, >= 15 bars) or the multi-day weekend session break.

## Findings

- [INFO] gaps: session break between 2026-08-14T23:54:00+00:00 and 2026-08-17T01:01:00+00:00 (expected)
- [INFO] gaps: session break between 2026-08-21T23:54:00+00:00 and 2026-08-24T01:01:00+00:00 (expected)
- [INFO] gaps: session break between 2026-08-28T23:54:00+00:00 and 2026-08-31T01:01:00+00:00 (expected)
- [INFO] gaps: session break between 2026-09-04T23:54:00+00:00 and 2026-09-07T01:01:00+00:00 (expected)
- [INFO] gaps: session break between 2026-09-11T23:54:00+00:00 and 2026-09-14T01:01:00+00:00 (expected)
- [INFO] gaps: session break between 2026-09-18T23:54:00+00:00 and 2026-09-21T01:01:00+00:00 (expected)
- [INFO] gaps: session break between 2026-09-25T23:54:00+00:00 and 2026-09-28T01:01:00+00:00 (expected)
- [INFO] gaps: session break between 2026-10-02T23:54:00+00:00 and 2026-10-05T01:01:00+00:00 (expected)
- [WARNING] gaps: gap: 2 bar(s) missing between 2026-08-14T01:37:00+00:00 and 2026-08-14T01:39:00+00:00 (outside signal windows)
- [WARNING] gaps: gap: 2 bar(s) missing between 2026-08-14T01:52:00+00:00 and 2026-08-14T01:54:00+00:00 (outside signal windows)
- [WARNING] gaps: gap: 2 bar(s) missing between 2026-08-14T02:10:00+00:00 and 2026-08-14T02:12:00+00:00 (outside signal windows)
- [WARNING] gaps: gap: 2 bar(s) missing between 2026-08-14T02:15:00+00:00 and 2026-08-14T02:17:00+00:00 (outside signal windows)
- [WARNING] gaps: gap: 2 bar(s) missing between 2026-08-14T06:33:00+00:00 and 2026-08-14T06:35:00+00:00 (outside signal windows)
- [WARNING] gaps: gap: 2 bar(s) missing between 2026-08-14T06:40:00+00:00 and 2026-08-14T06:42:00+00:00 (outside signal windows)
- [WARNING] gaps: gap: 2 bar(s) missing between 2026-08-14T06:53:00+00:00 and 2026-08-14T06:55:00+00:00 (outside signal windows)
- [WARNING] gaps: gap: 2 bar(s) missing between 2026-08-14T07:20:00+00:00 and 2026-08-14T07:22:00+00:00 (outside signal windows)
- [WARNING] gaps: gap: 2 bar(s) missing between 2026-08-14T08:41:00+00:00 and 2026-08-14T08:43:00+00:00 (outside signal windows)
- [WARNING] gaps: gap: 2 bar(s) missing between 2026-08-17T02:17:00+00:00 and 2026-08-17T02:19:00+00:00 (outside signal windows)
- [WARNING] gaps: gap: 2 bar(s) missing between 2026-08-17T02:41:00+00:00 and 2026-08-17T02:43:00+00:00 (outside signal windows)
- [WARNING] gaps: gap: 2 bar(s) missing between 2026-08-17T05:58:00+00:00 and 2026-08-17T06:00:00+00:00 (outside signal windows)
- [WARNING] gaps: gap: 2 bar(s) missing between 2026-08-17T06:11:00+00:00 and 2026-08-17T06:13:00+00:00 (outside signal windows)
- [WARNING] gaps: gap: 2 bar(s) missing between 2026-08-17T07:12:00+00:00 and 2026-08-17T07:14:00+00:00 (outside signal windows)
- [WARNING] gaps: gap: 2 bar(s) missing between 2026-08-17T07:58:00+00:00 and 2026-08-17T08:00:00+00:00 (outside signal windows)
- [WARNING] gaps: gap: 2 bar(s) missing between 2026-08-17T08:04:00+00:00 and 2026-08-17T08:06:00+00:00 (outside signal windows)
- [WARNING] gaps: gap: 2 bar(s) missing between 2026-08-17T08:17:00+00:00 and 2026-08-17T08:19:00+00:00 (outside signal windows)
- [WARNING] gaps: gap: 2 bar(s) missing between 2026-08-17T08:41:00+00:00 and 2026-08-17T08:43:00+00:00 (outside signal windows)
- [INFO] gaps: scheduled daily break (recurring 63-bar pattern) between 2026-08-17T23:58:00+00:00 and 2026-08-18T01:01:00+00:00
- [INFO] gaps: scheduled daily break (recurring 63-bar pattern) between 2026-08-18T23:58:00+00:00 and 2026-08-19T01:01:00+00:00
- [INFO] gaps: scheduled daily break (recurring 63-bar pattern) between 2026-08-19T23:58:00+00:00 and 2026-08-20T01:01:00+00:00
- [WARNING] gaps: gap: 2 bar(s) missing between 2026-08-20T01:43:00+00:00 and 2026-08-20T01:45:00+00:00 (outside signal windows)
- [WARNING] gaps: gap: 2 bar(s) missing between 2026-08-20T02:21:00+00:00 and 2026-08-20T02:23:00+00:00 (outside signal windows)
- [INFO] gaps: scheduled daily break (recurring 63-bar pattern) between 2026-08-20T23:58:00+00:00 and 2026-08-21T01:01:00+00:00
- [WARNING] gaps: gap: 2 bar(s) missing between 2026-08-24T02:04:00+00:00 and 2026-08-24T02:06:00+00:00 (outside signal windows)
- [INFO] gaps: scheduled daily break (recurring 63-bar pattern) between 2026-08-24T23:58:00+00:00 and 2026-08-25T01:01:00+00:00
- [WARNING] gaps: gap: 2 bar(s) missing between 2026-08-25T01:45:00+00:00 and 2026-08-25T01:47:00+00:00 (outside signal windows)
- [WARNING] gaps: gap: 2 bar(s) missing between 2026-08-25T01:49:00+00:00 and 2026-08-25T01:51:00+00:00 (outside signal windows)
- [INFO] gaps: scheduled daily break (recurring 63-bar pattern) between 2026-08-25T23:58:00+00:00 and 2026-08-26T01:01:00+00:00
- [WARNING] gaps: gap: 2 bar(s) missing between 2026-08-26T01:36:00+00:00 and 2026-08-26T01:38:00+00:00 (outside signal windows)
- [WARNING] gaps: gap: 2 bar(s) missing between 2026-08-26T01:53:00+00:00 and 2026-08-26T01:55:00+00:00 (outside signal windows)
- [WARNING] gaps: gap: 4 bar(s) missing between 2026-08-26T02:15:00+00:00 and 2026-08-26T02:19:00+00:00 (outside signal windows)
- [INFO] gaps: scheduled daily break (recurring 63-bar pattern) between 2026-08-26T23:58:00+00:00 and 2026-08-27T01:01:00+00:00
- [INFO] gaps: scheduled daily break (recurring 63-bar pattern) between 2026-08-27T23:58:00+00:00 and 2026-08-28T01:01:00+00:00
- [WARNING] gaps: gap: 2 bar(s) missing between 2026-08-28T02:40:00+00:00 and 2026-08-28T02:42:00+00:00 (outside signal windows)
- [WARNING] gaps: gap: 2 bar(s) missing between 2026-08-28T08:47:00+00:00 and 2026-08-28T08:49:00+00:00 (outside signal windows)
- [INFO] gaps: scheduled daily break (recurring 63-bar pattern) between 2026-08-31T23:58:00+00:00 and 2026-09-01T01:01:00+00:00
- [WARNING] gaps: gap: 2 bar(s) missing between 2026-09-01T01:25:00+00:00 and 2026-09-01T01:27:00+00:00 (outside signal windows)
- [WARNING] gaps: gap: 2 bar(s) missing between 2026-09-01T01:34:00+00:00 and 2026-09-01T01:36:00+00:00 (outside signal windows)
- [INFO] gaps: scheduled daily break (recurring 63-bar pattern) between 2026-09-01T23:58:00+00:00 and 2026-09-02T01:01:00+00:00
- [INFO] gaps: scheduled daily break (recurring 63-bar pattern) between 2026-09-02T23:58:00+00:00 and 2026-09-03T01:01:00+00:00
- [WARNING] gaps: gap: 2 bar(s) missing between 2026-09-03T02:27:00+00:00 and 2026-09-03T02:29:00+00:00 (outside signal windows)
- [INFO] gaps: scheduled daily break (recurring 63-bar pattern) between 2026-09-03T23:58:00+00:00 and 2026-09-04T01:01:00+00:00
- [WARNING] gaps: gap: 2 bar(s) missing between 2026-09-04T01:21:00+00:00 and 2026-09-04T01:23:00+00:00 (outside signal windows)
- [WARNING] gaps: gap: 2 bar(s) missing between 2026-09-04T02:14:00+00:00 and 2026-09-04T02:16:00+00:00 (outside signal windows)
- [WARNING] gaps: gap: 2 bar(s) missing between 2026-09-04T02:20:00+00:00 and 2026-09-04T02:22:00+00:00 (outside signal windows)
- [WARNING] gaps: gap: 2 bar(s) missing between 2026-09-04T02:42:00+00:00 and 2026-09-04T02:44:00+00:00 (outside signal windows)
- [WARNING] gaps: gap: 2 bar(s) missing between 2026-09-04T05:07:00+00:00 and 2026-09-04T05:09:00+00:00 (outside signal windows)
- [WARNING] gaps: gap: 2 bar(s) missing between 2026-09-04T05:52:00+00:00 and 2026-09-04T05:54:00+00:00 (outside signal windows)
- [WARNING] gaps: gap: 2 bar(s) missing between 2026-09-04T06:06:00+00:00 and 2026-09-04T06:08:00+00:00 (outside signal windows)
- [WARNING] gaps: gap: 2 bar(s) missing between 2026-09-04T07:22:00+00:00 and 2026-09-04T07:24:00+00:00 (outside signal windows)
- [WARNING] gaps: gap: 4 bar(s) missing between 2026-09-04T15:41:00+00:00 and 2026-09-04T15:45:00+00:00 (outside signal windows)
- [WARNING] gaps: gap: 2 bar(s) missing between 2026-09-04T15:46:00+00:00 and 2026-09-04T15:48:00+00:00 (outside signal windows)
- [WARNING] gaps: gap: 2 bar(s) missing between 2026-09-07T01:44:00+00:00 and 2026-09-07T01:46:00+00:00 (outside signal windows)
- [WARNING] gaps: gap: 2 bar(s) missing between 2026-09-07T01:46:00+00:00 and 2026-09-07T01:48:00+00:00 (outside signal windows)
- [WARNING] gaps: gap: 2 bar(s) missing between 2026-09-07T01:53:00+00:00 and 2026-09-07T01:55:00+00:00 (outside signal windows)
- [WARNING] gaps: gap: 2 bar(s) missing between 2026-09-07T02:08:00+00:00 and 2026-09-07T02:10:00+00:00 (outside signal windows)
- [WARNING] gaps: gap: 2 bar(s) missing between 2026-09-07T02:11:00+00:00 and 2026-09-07T02:13:00+00:00 (outside signal windows)
- [WARNING] gaps: gap: 2 bar(s) missing between 2026-09-07T03:28:00+00:00 and 2026-09-07T03:30:00+00:00 (outside signal windows)
- [WARNING] gaps: gap: 302 bar(s) missing between 2026-09-07T19:59:00+00:00 and 2026-09-08T01:01:00+00:00 (outside signal windows)
- [INFO] gaps: scheduled daily break (recurring 63-bar pattern) between 2026-09-08T23:58:00+00:00 and 2026-09-09T01:01:00+00:00
- [WARNING] gaps: gap: 2 bar(s) missing between 2026-09-09T01:35:00+00:00 and 2026-09-09T01:37:00+00:00 (outside signal windows)
- [WARNING] gaps: gap: 2 bar(s) missing between 2026-09-09T01:48:00+00:00 and 2026-09-09T01:50:00+00:00 (outside signal windows)
- [WARNING] gaps: gap: 2 bar(s) missing between 2026-09-09T02:06:00+00:00 and 2026-09-09T02:08:00+00:00 (outside signal windows)
- [WARNING] gaps: gap: 2 bar(s) missing between 2026-09-09T02:12:00+00:00 and 2026-09-09T02:14:00+00:00 (outside signal windows)
- [WARNING] gaps: gap: 2 bar(s) missing between 2026-09-09T02:16:00+00:00 and 2026-09-09T02:18:00+00:00 (outside signal windows)
- [INFO] gaps: scheduled daily break (recurring 63-bar pattern) between 2026-09-09T23:58:00+00:00 and 2026-09-10T01:01:00+00:00
- [WARNING] gaps: gap: 2 bar(s) missing between 2026-09-10T02:25:00+00:00 and 2026-09-10T02:27:00+00:00 (outside signal windows)
- [INFO] gaps: scheduled daily break (recurring 63-bar pattern) between 2026-09-10T23:58:00+00:00 and 2026-09-11T01:01:00+00:00
- [WARNING] gaps: gap: 2 bar(s) missing between 2026-09-11T02:28:00+00:00 and 2026-09-11T02:30:00+00:00 (outside signal windows)
- [INFO] gaps: scheduled daily break (recurring 63-bar pattern) between 2026-09-14T23:58:00+00:00 and 2026-09-15T01:01:00+00:00
- [WARNING] gaps: gap: 2 bar(s) missing between 2026-09-15T01:33:00+00:00 and 2026-09-15T01:35:00+00:00 (outside signal windows)
- [WARNING] gaps: gap: 2 bar(s) missing between 2026-09-15T01:40:00+00:00 and 2026-09-15T01:42:00+00:00 (outside signal windows)
- [WARNING] gaps: gap: 2 bar(s) missing between 2026-09-15T01:54:00+00:00 and 2026-09-15T01:56:00+00:00 (outside signal windows)
- [WARNING] gaps: gap: 2 bar(s) missing between 2026-09-15T02:24:00+00:00 and 2026-09-15T02:26:00+00:00 (outside signal windows)
- [INFO] gaps: scheduled daily break (recurring 63-bar pattern) between 2026-09-15T23:58:00+00:00 and 2026-09-16T01:01:00+00:00
- [WARNING] gaps: gap: 2 bar(s) missing between 2026-09-16T01:54:00+00:00 and 2026-09-16T01:56:00+00:00 (outside signal windows)
- [INFO] gaps: scheduled daily break (recurring 63-bar pattern) between 2026-09-16T23:58:00+00:00 and 2026-09-17T01:01:00+00:00
- [INFO] gaps: scheduled daily break (recurring 63-bar pattern) between 2026-09-17T23:58:00+00:00 and 2026-09-18T01:01:00+00:00
- [WARNING] gaps: gap: 2 bar(s) missing between 2026-09-18T02:31:00+00:00 and 2026-09-18T02:33:00+00:00 (outside signal windows)
- [WARNING] gaps: gap: 2 bar(s) missing between 2026-09-21T06:57:00+00:00 and 2026-09-21T06:59:00+00:00 (outside signal windows)
- [INFO] gaps: scheduled daily break (recurring 63-bar pattern) between 2026-09-21T23:58:00+00:00 and 2026-09-22T01:01:00+00:00
- [WARNING] gaps: gap: 2 bar(s) missing between 2026-09-22T06:25:00+00:00 and 2026-09-22T06:27:00+00:00 (outside signal windows)
- [WARNING] gaps: gap: 2 bar(s) missing between 2026-09-22T06:27:00+00:00 and 2026-09-22T06:29:00+00:00 (outside signal windows)
- [INFO] gaps: scheduled daily break (recurring 63-bar pattern) between 2026-09-22T23:58:00+00:00 and 2026-09-23T01:01:00+00:00
- [WARNING] gaps: gap: 2 bar(s) missing between 2026-09-23T02:33:00+00:00 and 2026-09-23T02:35:00+00:00 (outside signal windows)
- [WARNING] gaps: gap: 2 bar(s) missing between 2026-09-23T05:52:00+00:00 and 2026-09-23T05:54:00+00:00 (outside signal windows)
- [WARNING] gaps: gap: 2 bar(s) missing between 2026-09-23T07:43:00+00:00 and 2026-09-23T07:45:00+00:00 (outside signal windows)
- [INFO] gaps: scheduled daily break (recurring 63-bar pattern) between 2026-09-23T23:58:00+00:00 and 2026-09-24T01:01:00+00:00
- [INFO] gaps: scheduled daily break (recurring 63-bar pattern) between 2026-09-24T23:58:00+00:00 and 2026-09-25T01:01:00+00:00
- [INFO] gaps: scheduled daily break (recurring 63-bar pattern) between 2026-09-28T23:58:00+00:00 and 2026-09-29T01:01:00+00:00
- [WARNING] gaps: gap: 2 bar(s) missing between 2026-09-29T02:03:00+00:00 and 2026-09-29T02:05:00+00:00 (outside signal windows)
- [INFO] gaps: scheduled daily break (recurring 63-bar pattern) between 2026-09-29T23:58:00+00:00 and 2026-09-30T01:01:00+00:00
- [INFO] gaps: scheduled daily break (recurring 63-bar pattern) between 2026-09-30T23:58:00+00:00 and 2026-10-01T01:01:00+00:00
- [INFO] gaps: scheduled daily break (recurring 63-bar pattern) between 2026-10-01T23:58:00+00:00 and 2026-10-02T01:01:00+00:00
- [INFO] dst: zoneinfo offsets agree with explicit US DST rules
- [WARNING] or_coverage: 2026-08-13: OR window missing 15/15 bars (09:30, 09:31, 09:32, 09:33, 09:34...) -> NO TRADE that day
- [WARNING] or_coverage: 2026-08-16: OR window missing 15/15 bars (09:30, 09:31, 09:32, 09:33, 09:34...) -> NO TRADE that day
- [WARNING] or_coverage: 2026-08-23: OR window missing 15/15 bars (09:30, 09:31, 09:32, 09:33, 09:34...) -> NO TRADE that day
- [WARNING] or_coverage: 2026-08-30: OR window missing 15/15 bars (09:30, 09:31, 09:32, 09:33, 09:34...) -> NO TRADE that day
- [WARNING] or_coverage: 2026-09-06: OR window missing 15/15 bars (09:30, 09:31, 09:32, 09:33, 09:34...) -> NO TRADE that day
- [WARNING] or_coverage: 2026-09-13: OR window missing 15/15 bars (09:30, 09:31, 09:32, 09:33, 09:34...) -> NO TRADE that day
- [WARNING] or_coverage: 2026-09-20: OR window missing 15/15 bars (09:30, 09:31, 09:32, 09:33, 09:34...) -> NO TRADE that day
- [WARNING] or_coverage: 2026-09-27: OR window missing 15/15 bars (09:30, 09:31, 09:32, 09:33, 09:34...) -> NO TRADE that day
- [WARNING] or_coverage: 2026-10-04: OR window missing 15/15 bars (09:30, 09:31, 09:32, 09:33, 09:34...) -> NO TRADE that day
- [WARNING] or_coverage: 2026-10-05: OR window missing 15/15 bars (09:30, 09:31, 09:32, 09:33, 09:34...) -> NO TRADE that day
- [WARNING] trade_coverage: 2026-10-05: partial trading day, data ends before 11:30 NY (missing 105/105 bars)
- [INFO] coverage: 50000 bars across 46 NY day(s), 2026-08-13..2026-10-05

Real broker-data audit: EXECUTED on 50000 bars (US30). No gaps intersect the signal windows unless listed above as ERROR.
