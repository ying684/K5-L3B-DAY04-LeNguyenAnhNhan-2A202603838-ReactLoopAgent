# Ghi chú phân tích · Day 04

Họ và tên: LeNguyenAnhNhan  
MSSV: 2A202603838

## 1. Case được chọn

Em chọn case **E4**: xác định các component bị ảnh hưởng trong incident GitHub `xr3myzj7ms51` và kiểm tra Actions có liên quan hay không.

Ở lần đánh giá trước cải tiến, agent đọc được chi tiết incident nhưng câu trả lời chỉ ghi tên tool làm nguồn, không dẫn URL incident. Case đạt **94/100**. Em chọn lỗi này để bổ sung kiểm tra nguồn trước khi agent kết thúc.

## 2. Bằng chứng trong trace

Trong case E4 của `eval_before.json`, tool `get_incident_details` trả về URL nguồn. Các trường liên quan được trích rút gọn như sau:

```json
{
  "name": "get_incident_details",
  "arguments": {
    "provider": "github",
    "incident_id": "xr3myzj7ms51"
  },
  "result": {
    "ok": true,
    "url": "https://stspg.io/pjgptg3cfc6n"
  }
}
```

Tuy nhiên, câu trả lời chỉ ghi `Source: functions.get_incident_details output` và không chứa URL trên. Agent vẫn trả `completed` vì model đã báo `finish: stop`.

Nguyên nhân ở vòng lặp là chưa kiểm tra URL trước khi nhận câu trả lời cuối. Yêu cầu dẫn nguồn trong system prompt chưa bảo đảm model thực hiện đúng.

## 3. Thay đổi đã thực hiện

Trong `agent.py`, em bổ sung bước kiểm tra nguồn:

- Lưu URL của các lần gọi `get_incident_details` thành công.
- Khi model trả câu trả lời cuối, kiểm tra các URL đã quan sát có xuất hiện hay không.
- Nếu thiếu, ghi event `validation_missing_source` và yêu cầu model bổ sung trong giới hạn `max_steps`.
- Không yêu cầu URL từ incident lấy thất bại. Nếu hết lượt mà câu trả lời vẫn thiếu nguồn, trả `max_steps`.

Ngoài ra, em làm rõ prompt về giới hạn snapshot, phạm vi ảnh hưởng, cách xử lý timeout và việc theo liên kết incident khi cần thêm bằng chứng. Vòng lặp có lời nhắc dành lượt cuối để trả lời, hạn chế đọc quá nhiều incident.

Các tests kiểm tra URL, xử lý lỗi, nhiều tool calls và giới hạn bước đều pass. Fixtures, cases, scenarios, grading và rubric được giữ nguyên.

## 4. So sánh hai lần chạy

Bảng dưới sử dụng kết quả trong `eval_before.json` và `eval_after.json`. Hai report cùng dùng Groq với `openai/gpt-oss-20b` cho agent và judge, dataset core, snapshot cố định, tối đa **8 bước** và **8.192 token output** mỗi lần gọi model.

| Chỉ số | Trước cải tiến | Sau cải tiến |
|---|---:|---:|
| Case được chấm | 22/22 | 22/22 |
| Điểm tổng | 89,68 | 89,86 |
| Điểm E4 | 94 | 100 |
| Số lần gọi model của agent | 67 | 67 |
| Số tool calls | 46 | 46 |
| Token của agent | 84.677 | 116.637 |
| Token của judge | 48.523 | 44.517 |
| Tổng token | 133.200 | 161.154 |

Sau cải tiến, câu trả lời E4 có URL `https://stspg.io/pjgptg3cfc6n`. Trong lượt eval này, model tự dẫn đủ URL nên không kích hoạt event yêu cầu sửa nguồn. Hành vi yêu cầu sửa khi thiếu URL được kiểm tra bằng tests offline.

Ở H6, agent đọc thêm incident liên quan để tìm nguyên nhân, thay vì dừng ở incident ban đầu. Tuy vậy, A1 vẫn dùng hết số bước và H7 vẫn kết luận Cloudflare operational khi tool timeout. Các lỗi này chưa được giải quyết trong phiên bản được đánh giá.

Điểm tổng tăng **0,18 điểm**, nhưng tổng token tăng **27.954 token**, khoảng **20,99%**. Số model calls không giảm, nên kết quả chưa cho thấy cải thiện chi phí. Không có dữ liệu billing để quy đổi chính xác ra tiền.

## 5. Giới hạn

- Điểm LLM judge là ước lượng. Agent và judge dùng cùng model nên có thể thiên lệch; cần đọc answer và trace cùng với điểm.
- Việc so sánh một cặp report không đủ chứng minh độ ổn định. Vì đồng thời sửa validation, prompt và lời nhắc budget, không thể tách riêng tác dụng của từng thay đổi.
- Baseline có một lần retry E6 chưa chấm được do lỗi provider. Lịch sử retry và bản sao trước retry được giữ lại; 21 case đã có điểm không thay đổi.
- Snapshot bài chính được lưu ngày 09/11/2026, không phản ánh trạng thái thời gian thực. Tool chỉ tìm trong 50 incident gần nhất và có thể lược bớt updates hoặc cắt nội dung.
- Validation URL chỉ kiểm tra nguồn có mặt trong câu trả lời, không bảo đảm mọi nhận định đúng. Agent vẫn có thể suy diễn sai phạm vi, thời gian hoặc trạng thái sau lỗi.
- Tests offline kiểm tra các tình huống được mô phỏng, không bảo đảm model thật luôn tuân thủ chỉ dẫn. Agent còn lỗi cần tiếp tục cải thiện.

## 6. Phần bonus

Em mở rộng agent để sử dụng `tools.schemas` và `tools.system_prompt` cho GitHub, Cloudflare, Vercel, npm và DigitalOcean.

**Retry:** agent nhận lỗi `INVALID_ARGUMENTS` để model sửa tham số. Với 429, agent theo dõi theo provider, cho phép thử lại một lần sau lỗi đầu và dừng gọi backend khi lỗi tiếp tục. Agent đọc `Retry-After` dạng số giây hoặc HTTP date; giới hạn chờ 5 giây/lần và tổng 10 giây/run. Các tình huống chờ được kiểm tra bằng mocks; eval dùng lỗi 429 giả lập với thời gian chờ bằng 0.

**Pagination và context:** khi còn `next_offset`, agent nhắc model đọc tiếp nếu chưa tìm thấy thông báo cần thiết. Danh sách `distractors` được bỏ khỏi context gửi model nhưng giữ nguyên trong trace để đối chiếu.

Kết quả trong `eval_bonus.json` dùng cùng agent/judge model, tối đa **16 bước**, đủ **10/10 case** được chấm:

| Case | B1 | B2 | B3 | B4 | B5 | B6 | B7 | B8 | B9 | B10 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Điểm | 100 | 100 | 100 | 83 | 57 | 50 | 100 | 96 | 65 | 88 |

Điểm bộ bonus là **83,9/100**, quy đổi **12,59/15 điểm tham khảo**. Tổng cộng có **39 model calls**, **100.490 agent tokens** và **32.348 judge tokens**.

Trace B2 cho thấy agent đọc hai trang timeline; B3 phục hồi sau một lần 429; B4 dừng sau hai lần rate limit và báo chưa xác nhận trạng thái Vercel. B6 còn thiếu bước đọc chi tiết incident nên bị áp trần 50 điểm. B10 chưa trình bày đầy đủ quá trình retry và có kết luận quá rộng về ảnh hưởng tới hệ thống người dùng.

Một số lời chấm cần kiểm tra lại: B4 bị trừ vì chỉ thử hai lần dù yêu cầu là tối đa ba; B5 bị nhận xét thiếu URL trong khi answer có URL. Em giữ nguyên điểm và đối chiếu bằng trace, không tự điều chỉnh kết quả.

Sau khi bổ sung bonus, **57 tests trong thư mục tests và 3 tests agent bonus đều pass**. Code của các phiên bản đã đánh giá được lưu trong `artifacts/`; các report chính không thay đổi khi bổ sung bonus.
