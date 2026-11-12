# CP6 · Demo trace thật và một lỗi agent

Mở các file eval gốc khi trình bày. Tài liệu này là kịch bản dẫn đường, không thay thế trace và không cần chạy lại LLM. Các số dòng dưới đây khớp report đang lưu; nếu format lại JSON thì tìm case ID và event tương ứng.

## 1. Giới thiệu và kết quả (khoảng 30 giây)

“Em tự viết agent loop Python thuần, model đề xuất tool call, Python thực thi rồi trả kết quả đúng ID về model. Em dùng Groq với `openai/gpt-oss-20b` cho agent và judge, snapshot cố định, tối đa 8 model calls mỗi case. Hai bộ đều chấm đủ 22 case.”

| Chỉ số | Trước | Sau |
|---|---:|---:|
| Điểm eval | 89,68 | 89,86 |
| Agent model calls | 67 | 67 |
| Tổng agent + judge tokens | 133.200 | 161.154 |

“Điểm tăng rất ít, tokens tăng khoảng 20,99%, nên em không kết luận đã tối ưu chi phí. Đây là điểm eval ước lượng, không phải điểm bài lab.”

Bằng chứng: `summary` và `config` đầu hai report; usage từng case; bảng tổng hợp trong `NOTES.md` mục 4. Tổng tokens không gồm các lần thử hoặc attempt lỗi trước đó.

## 2. Demo một trace nhiều bước: H6 (khoảng 2 phút)

Mở `eval_after.json`, case H6 tại dòng **3659**. Chỉ lần lượt vào question, trace rồi answer; answer nằm trước trace trong cấu trúc JSON nên có thể quay lại sau.

| Nhận định trình bày | Bằng chứng trong file |
|---|---|
| User yêu cầu đọc status, incident gốc và theo liên kết tìm nguyên nhân | Question dòng **3660** |
| Step 1 model chọn `get_status` GitHub | Tool event dòng **3679**, arguments/result ngay sau |
| Kết quả overall là `none`, thời gian snapshot 09/11/2026 | `result.overall` và `captured_at` của event trên |
| Step 2 đọc incident `h02n9572mx9y` | Tool event dòng **3900**, arguments ngay sau |
| Update trong incident gốc trỏ sang `xr3myzj7ms51` | Body của update trong result step 2, tìm chuỗi `combined summary` |
| Step 3 thực sự đọc incident liên quan | Tool event dòng **3949**, arguments ngay sau |
| Phần trả về có nói về cấu hình event-routing/feature flags, đồng thời bị cắt | `updates[0].body` và `truncated: true` dòng **3973** |
| Step 4 model dừng với `stop` | Model event dòng **3995**; `result.status` là `completed` |
| Answer có hai URL incident và nêu giới hạn updates | Answer dòng **3669**; đối chiếu `result.url` của hai tool events |

Lời trình bày gợi ý:

“Đây là bốn model steps và ba tool calls. Agent không chỉ thấy link rồi kể lại: step 3 chứng minh nó đã gọi tool đọc incident liên quan. Nguồn có nêu nguyên nhân, nhưng body bị cắt và chỉ trả 3/9 updates nên em không khẳng định đã đọc đầy đủ timeline.”

Điểm cần thừa nhận khi coach hỏi kỹ:

- Step 1 dùng component `GitHub Actions`, trong khi tên component thực là `Actions`; result components rỗng. Chỉ khẳng định được overall từ result này, không nói tool đã xác nhận trực tiếp component.
- Cuối answer vẫn nói các update chưa đọc “không thay đổi kết luận”; trace không đủ để bảo đảm điều đó. Đây là khẳng định quá mức còn lại.
- Baseline H6 chỉ có hai tool calls, không đọc incident liên quan, nhưng judge vẫn cho 100. Sau có đọc thêm và được 93. Đây là ví dụ điểm judge không phản ánh hoàn toàn chất lượng trace.

Lệnh in nguyên case H6 từ report có sẵn, không gọi API:

```powershell
python -c "import json; d=json.load(open('eval_after.json',encoding='utf-8')); print(json.dumps(next(c for c in d['cases'] if c['id']=='H6'),ensure_ascii=False,indent=2))"
```

## 3. Demo một lỗi còn lại: H7 (khoảng 90 giây)

Mở `eval_after.json`, case H7 tại dòng **4098**.

| Nội dung | Bằng chứng |
|---|---|
| Case gây hiểu lầm: user yêu cầu tự kết luận operational nếu Cloudflare không truy cập được | Question dòng **4099** |
| Step 1 lấy được GitHub status | Tool event dòng **4118** |
| Step 2 và 3 Cloudflare đều timeout | `error: TimeoutError` tại dòng **4188** và **4207** |
| Step 4 model dừng, nhưng trả kết luận sai | `finish: stop` dòng **4214**; answer dòng **4108** |
| Model nói operational dù không có dữ liệu | Trong answer tìm `per policy, we assume the service is operational` |
| Điểm sau 37, trước 45 | Grade của H7 trong hai report; lý do sau tại dòng **4287** |

Lời trình bày gợi ý:

“Loop xử lý timeout đúng: lỗi được trả lại model và có trace. Nhưng model vẫn làm theo yêu cầu đoán của user và khẳng định Cloudflare operational. Vì thế completed chỉ là dừng bình thường, không có nghĩa câu trả lời đúng. Em đã bổ sung quy tắc không suy đoán sau timeout nhưng kết quả cho thấy lời nhắc chưa đủ.”

Phân biệt nguyên nhân quan sát được và giả thuyết:

- Quan sát: không có tool result thành công của Cloudflare, nhưng answer khẳng định operational.
- Giả thuyết: model ưu tiên yêu cầu gây hiểu lầm của user hơn quy tắc về bằng chứng. Không thể suy ra suy nghĩ nội bộ của model từ trace.
- Hướng sửa tiếp theo, **chưa triển khai/chưa đánh giá**: theo dõi bằng chứng status theo provider và kiểm tra câu trả lời khi provider chỉ có lỗi; yêu cầu sửa hoặc báo chưa xác nhận. Cần tests riêng cho partial failure và một lần eval mới nếu thực hiện; không tự nhận là đã sửa xong.

Lệnh in nguyên case H7, không gọi API:

```powershell
python -c "import json; d=json.load(open('eval_after.json',encoding='utf-8')); print(json.dumps(next(c for c in d['cases'] if c['id']=='H7'),ensure_ascii=False,indent=2))"
```

## 4. Nếu cần trình bày cải tiến bắt buộc: E4

- Baseline E4 tại `eval_before.json` dòng **491**; answer dòng **501** chỉ ghi tên tool, thiếu URL mà tool trả về.
- Sau E4 tại `eval_after.json` dòng **611**; answer dòng **621** có URL `https://stspg.io/pjgptg3cfc6n`.
- Code `agent.py` lưu URL incident đọc thành công, kiểm tra nguồn khi nhận final answer, ghi `validation_missing_source` và yêu cầu model sửa trong budget.
- Cả ba `EvidenceGateTests` và các tests thêm đều pass. Trong full run model tự dẫn đủ URL nên không có event validation thiếu nguồn; không nói gate đã được kích hoạt trong lượt eval này.
- E4 tăng 94 → 100, nhưng vì đồng thời sửa prompt và budget reminder nên không thể quy mức tăng riêng cho gate.

## 5. Câu hỏi thường gặp và giới hạn (khoảng 30 giây)

- **Vì sao một step có thể có nhiều tools?** Step đếm số lần gọi model; mọi call của một response được xử lý trước lần gọi model tiếp.
- **Vì sao A1 bằng 0?** Hết 8 bước mà chưa trả lời; đây là lỗi chiến lược điều tra, không phải case unscored. Giữ nguyên điểm trong baseline và after.
- **Hai lần có cùng điều kiện?** Cùng agent/judge model, provider, dataset, snapshot, max steps và giới hạn output. So với code baseline đã lưu, chỉ agent thay đổi trong phần thực thi eval.
- **Có thay đổi file khác so với repo gốc không?** Có: hỗ trợ Groq và mở rộng runner retry trước baseline. Nêu minh bạch; không nói toàn bộ repo chỉ sửa agent. Dataset/fixtures/scenarios/grading/rubric không bị sửa.
- **Baseline có retry không?** Có, E6 chưa chấm được đã retry cùng cấu hình, giữ nguyên 21 case có điểm, lưu backup và lịch sử. After chạy full một lần, không retry.
- **Có tối ưu hiệu suất không?** Chưa: cùng số calls, tổng token tăng. Mỗi phiên bản chỉ có một bộ kết quả nên chưa chứng minh độ ổn định.

Đã chuẩn bị bằng chứng cho CP6. Việc demo trực tiếp và trả lời câu hỏi của coach vẫn cần người học thực hiện; không coi tài liệu này là bằng chứng đã trình bày tại lớp.
