# Rà soát và dọn thư mục nộp bài

Đối chiếu README, RULES, GUIDE, RUBRIC, SUBMISSION và checklist trên slide. Kết quả kiểm tra ngày 12/11/2026, theo GMT+7. Chưa commit/push hoặc nộp LMS trong quá trình rà soát này.

## 1. Checklist đã kiểm tra

| Yêu cầu | Trạng thái và bằng chứng |
|---|---|
| Đúng tên repo | Đạt mẫu L3B: `K5-L3B-DAY04-LeNguyenAnhNhan-2A202603838-ReactLoopAgent` |
| Repo riêng, public | GitHub API công khai xác nhận `ying684/K5-L3B-DAY04-LeNguyenAnhNhan-2A202603838-ReactLoopAgent`, `private=false`, `visibility=public`, `fork=true` |
| README ghi Bài cá nhân | Đạt, đầu README có “Hình thức: Bài cá nhân” |
| Có agent.py và hai eval chính | Có; 22/22 case ở cả hai report, không còn unscored |
| Điểm tổng khác null | Before 89,68; after 89,86 |
| Cùng cấu hình trước/sau | Cùng Groq/model cho agent và judge, dataset core, snapshot, 8 bước và output budget 8192 |
| NOTES đủ 5 mục | Có, thêm mục 6 phân tích bonus; có evidence, thay đổi, số liệu và giới hạn |
| Tests pass | 57 tests trong tests/ và 3 tests agent bonus đều pass sau dọn; không gọi API |
| Không đưa .env/API key lên Git | .env giữ local ở root và được .gitignore loại trừ; git ls-files chỉ có .env.example; đối chiếu giá trị key đang dùng không thấy trong các file bài nộp |
| Không sửa fixtures/cases/scenarios/grading/rubric | Đã đối chiếu nội dung với Git HEAD, các file được bảo vệ giữ nguyên |
| Bonus | Có eval_bonus.json, đủ 10/10 case, 83,9/100; bonus tham khảo 12,59/15 |
| Demo | Có DEMO.md dẫn đến trace thật H6/H7 và vị trí trong report; người học vẫn cần tự trình bày |
| Bản cuối đã commit/push | Chưa: working tree còn file sửa/thêm, kiểm tra git status trước khi nộp |
| Đã dán link LMS đúng lớp | Chưa xác nhận/không thực hiện; người học phải nộp ở lớp L3B |

Không có key đang dùng trong các file đã kiểm tra không chứng minh mọi dạng dữ liệu nhạy cảm đều đã được loại trừ. Không tự khẳng định đã rà sạch toàn bộ lịch sử Git.

## 2. Các file giữ lại và lý do

Giữ đủ **32 file gốc được Git theo dõi**, kể cả tài liệu, ảnh sơ đồ, tests, tools và dữ liệu do giảng viên cung cấp. SUBMISSION yêu cầu giữ các file còn lại của repo đề; không xóa file gốc chỉ vì không trực tiếp xuất hiện trong báo cáo.

### Bài nộp và báo cáo chính

- `agent.py`: phiên bản cuối có nhánh bonus.
- `eval_before.json`, `eval_after.json`: hai report chính, giữ nguyên bytes/kết quả đã chạy.
- `eval_bonus.json`: report bonus, giữ nguyên bytes/kết quả đã chạy.
- `NOTES.md`: phân tích đủ 5 mục và phần bonus.
- `DEMO.md`: hướng dẫn mở trace thật, trình bày lỗi và giới hạn.
- `SUBMISSION_CHECKLIST.md`: danh sách dọn dẹp và việc còn cần hoàn tất.

### Code chạy, tools và bộ chấm

- `providers.py`, `run.py`, `status_tools.py`.
- `evals/run_evals.py`, `evals/grading.py`, `evals/scenarios.py`, `evals/cases.json`.
- `bonus/__init__.py`, `bonus/tools.py`, `bonus/test_agent.py`, `bonus/cases.json`.

### Dữ liệu snapshot và sơ đồ gốc

- `fixtures/github.json`, `fixtures/cloudflare.json`.
- `bonus/fixtures/digitalocean.json`, `bonus/fixtures/npm.json`, `bonus/fixtures/vercel.json`.
- `assets/agent-architecture.svg`, `assets/lab-workflow.svg` (được README sử dụng).

### Tests giữ lại

- Tests gốc: `tests/test_bonus.py`, `tests/test_grading.py`, `tests/test_lab.py`, `tests/test_validation.py`.
- Tests bổ sung: `tests/test_cp2.py`, `tests/test_cp4.py`, `tests/test_eval_retry.py`, `tests/test_bonus_control.py`.
- Giữ tests bổ sung vì kiểm tra xử lý exception, source validation nhiều provider, giữ nguyên điểm khi retry, Retry-After và context/pagination; không phải file thử API dùng một lần.

### Tài liệu và cấu hình mẫu

- `README.md`, `GUIDE.md`, `RULES.md`, `RUBRIC.md`, `SUBMISSION.md`, `CHECKPOINTS.md`.
- `.gitignore`, `.env.example` (chỉ chứa placeholders, không phải secret).
- `.git/` giữ nguyên để quản lý repo; không coi đây là cache cần dọn. Không cần đưa `.git/` vào file ZIP nếu sau này tự tạo gói nộp, nhưng bài này yêu cầu nộp link repo.

### Bằng chứng phiên bản cần giữ

- `artifacts/cp3_baseline/agent.py` và `manifest.json`: code baseline trước cải tiến và mã SHA-256 đối chiếu.
- `artifacts/cp4_candidate/agent.py` và `manifest.json`: code đúng phiên bản đã chạy `eval_after.json` trước khi thêm nhánh bonus.
- `artifacts/bonus_candidate/manifest.json`: mã SHA-256 của `agent.py` ở root và report bonus; bản code bonus trùng root đã xóa.
- `eval_before.before_retry_20261112T040832765478Z.json`: bằng chứng report trước retry E6. Trường `retry_history.backup` trong `eval_before.json` tham chiếu đúng tên này, nên giữ file nguyên vị trí để đối chiếu. Không sửa tay report chỉ để dọn tên file.

Tổng sau dọn và thêm checklist: **47 file bài nộp ngoài .git/ và .env**, gồm 32 file gốc và 15 file bài làm/bằng chứng bổ sung. Có thêm .env local được Git ignore, không đưa vào bài nộp.

## 3. Đã xóa

Các file sau không phải file gốc được Git theo dõi. Code trùng được kiểm tra hash trước khi xóa:

| File | Lý do |
|---|---|
| `CP3_REVIEW.md` | Nội dung quan trọng đã nằm trong NOTES và checklist, tránh nhiều bản tổng kết trùng |
| `eval_before_incomplete.json` | Bộ eval thiếu điểm cũ trước khi chốt cấu hình output, không phải baseline cuối; lịch sử lỗi và giới hạn đã ghi trong NOTES |
| `eval_results_e2.json` | Chạy thử một case, không phải report nộp |
| `eval_results_a6.json` | Chạy thử một case, không phải report nộp |
| `artifacts/cp3_baseline/providers.py` | Trùng hoàn toàn providers.py hiện tại; manifest vẫn giữ hash |
| `artifacts/cp3_baseline/run.py` | Trùng hoàn toàn run.py hiện tại; manifest vẫn giữ hash |
| `artifacts/cp3_baseline/evals/run_evals.py` | Trùng hoàn toàn evals/run_evals.py hiện tại; manifest vẫn giữ hash |
| `artifacts/bonus_candidate/agent.py` | Trùng hoàn toàn agent.py cuối ở root; manifest vẫn giữ hash |

Xóa thêm **13 file .pyc** trong bốn thư mục `__pycache__/` ở root, bonus/, evals/ và tests/, cùng các thư mục cache rỗng. Xóa thư mục `artifacts/cp3_baseline/evals/` sau khi không còn file.

Tổng: **21 file, 404.183 bytes (~394,71 KiB)**. Không xóa file gốc của đề, ba report cuối hoặc bằng chứng retry được tham chiếu.

## 4. Cấu hình local và Git ignore

Nộp bằng link Git nên không cần chuyển .env ra ngoài project. File đã được đưa lại root, giữ nguyên nội dung và được .gitignore loại trừ. Git chỉ theo dõi .env.example. Không dùng git add -f cho .env.

Nếu cần chạy local ở terminal mới, nạp .env tại root:

```powershell
Get-Content '.env' | ForEach-Object {
    if ($_ -match '^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*?)\s*$') {
        [Environment]::SetEnvironmentVariable($matches[1], $matches[2].Trim().Trim('"').Trim("'"), 'Process')
    }
}
```

Không cần key để chạy kiểm tra offline. Dùng `-B` để không tạo lại cache:

```powershell
python -B -m unittest discover -s tests -v
python -B -m unittest discover -s bonus -p 'test_*.py' -v
```

## 5. Các điểm phải trình bày trung thực khi nộp

- Có thay đổi ngoài agent.py so với repo đề: providers.py/run.py để hỗ trợ Groq; runner để ghi cấu hình và retry unscored; README/.env.example để mô tả provider. Các thay đổi này đã tồn tại trước baseline cuối, nhưng khác hướng dẫn “giữ nguyên các file còn lại”. Không nói chỉ agent.py thay đổi so với repo gốc.
- CP4 sửa nhiều yếu tố cùng lúc (validation, prompt, nhắc budget), khác phương pháp một thay đổi trên slide. Không quy mức tăng điểm riêng cho một yếu tố.
- Baseline có retry E6, có backup/lịch sử; after và bonus mỗi bộ chạy một lượt, không chọn lại điểm thấp.
- A1/H7 và B6 còn lỗi; điểm eval và bonus là tham khảo, không phải điểm bài lab chính thức.
- Tên họ trong NOTES đang theo dạng không dấu của tên repo. Người học kiểm tra lại cách viết đầy đủ nếu cần trước khi nộp.
- Chưa tự xác minh thông báo deadline riêng của coach hoặc thời điểm nộp LMS. Theo SUBMISSION, ca 16:30–20:00 có hạn 12:00 trưa ngày hôm sau nếu không có thông báo khác.
- Sau commit/push, kiểm tra repo khi chưa đăng nhập có đủ ba report, NOTES, code và bằng chứng. Nộp link repo đúng lớp L3B trên LMS; không nộp link repo đề gốc.
