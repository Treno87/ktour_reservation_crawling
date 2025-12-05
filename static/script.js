// DOM 요소
const form = document.getElementById('crawling-form');
const startBtn = document.getElementById('start-btn');
const quickTodayBtn = document.getElementById('quick-today-btn');
const progressSection = document.getElementById('progress-section');
const resultSection = document.getElementById('result-section');
const progressBar = document.getElementById('progress-bar');
const progressCount = document.getElementById('progress-count');
const progressTotal = document.getElementById('progress-total');
const progressPercent = document.getElementById('progress-percent');
const currentDate = document.getElementById('current-date');
const statusMessage = document.getElementById('status-message');
const resultMessage = document.getElementById('result-message');
const downloadBtn = document.getElementById('download-btn');
const filesList = document.getElementById('files-list');
const refreshFilesBtn = document.getElementById('refresh-files-btn');

// 상태 관리
let statusCheckInterval = null;
let resultFilePath = null;

// 오늘 날짜로 설정
function setTodayDate() {
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('start_date').value = today;
    document.getElementById('end_date').value = today;
}

// 페이지 로드 시 실행
document.addEventListener('DOMContentLoaded', () => {
    setTodayDate();
    loadFilesList();

    // 구글 시트 체크박스 이벤트
    const googleSheetsCheckbox = document.getElementById('google_sheets');
    const sheetsUrlGroup = document.getElementById('sheets-url-group');

    googleSheetsCheckbox.addEventListener('change', () => {
        if (googleSheetsCheckbox.checked) {
            sheetsUrlGroup.style.display = 'block';
        } else {
            sheetsUrlGroup.style.display = 'none';
        }
    });
});

// 빠른 시작 버튼
quickTodayBtn.addEventListener('click', () => {
    setTodayDate();
    form.dispatchEvent(new Event('submit'));
});

// 폼 제출
form.addEventListener('submit', async (e) => {
    e.preventDefault();

    // 폼 데이터 수집
    const formData = {
        store_name: document.getElementById('store_name').value,
        start_date: document.getElementById('start_date').value,
        end_date: document.getElementById('end_date').value,
        mode: document.querySelector('input[name="mode"]:checked').value,
        output_format: document.getElementById('output_format').value,
        google_sheets: document.getElementById('google_sheets').checked,
        sheets_url: document.getElementById('sheets_url').value
    };

    // 구글 시트 옵션 검증
    if (formData.google_sheets && !formData.sheets_url) {
        alert('구글 시트 URL을 입력해주세요.');
        return;
    }

    // 날짜 유효성 검증
    const startDate = new Date(formData.start_date);
    const endDate = new Date(formData.end_date);

    if (startDate > endDate) {
        alert('시작 날짜는 종료 날짜보다 이전이어야 합니다.');
        return;
    }

    // 크롤링 시작 요청
    try {
        const response = await fetch('/api/start', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        const data = await response.json();

        if (data.success) {
            // UI 업데이트
            startBtn.disabled = true;
            quickTodayBtn.disabled = true;
            progressSection.style.display = 'block';
            resultSection.style.display = 'none';

            // 상태 체크 시작
            startStatusCheck();
        } else {
            alert(data.message);
        }
    } catch (error) {
        alert('크롤링 시작 중 오류가 발생했습니다: ' + error.message);
    }
});

// 상태 체크 시작
function startStatusCheck() {
    // 기존 인터벌 정리
    if (statusCheckInterval) {
        clearInterval(statusCheckInterval);
    }

    // 1초마다 상태 체크
    statusCheckInterval = setInterval(checkStatus, 1000);

    // 즉시 한 번 실행
    checkStatus();
}

// 상태 체크
async function checkStatus() {
    try {
        const response = await fetch('/api/status');
        const status = await response.json();

        // 진행률 업데이트
        updateProgress(status);

        // 크롤링 완료 시
        if (!status.is_running && status.progress > 0) {
            clearInterval(statusCheckInterval);
            statusCheckInterval = null;

            // 완료 UI 표시
            showResult(status);

            // 버튼 활성화
            startBtn.disabled = false;
            quickTodayBtn.disabled = false;

            // 파일 목록 새로고침
            loadFilesList();
        }
    } catch (error) {
        console.error('상태 체크 오류:', error);
    }
}

// 진행률 업데이트
function updateProgress(status) {
    const progress = status.progress;
    const total = status.total;
    const percent = total > 0 ? Math.round((progress / total) * 100) : 0;

    // 진행 바
    progressBar.style.width = percent + '%';

    // 텍스트
    progressCount.textContent = progress;
    progressTotal.textContent = total;
    progressPercent.textContent = percent;

    // 현재 날짜
    currentDate.textContent = status.current_date || '-';

    // 상태 메시지
    statusMessage.textContent = status.message;

    // 결과 파일 경로 저장
    if (status.result_file) {
        resultFilePath = status.result_file;
    }
}

// 결과 표시
function showResult(status) {
    resultSection.style.display = 'block';

    if (status.result_file) {
        resultMessage.textContent = status.message;
        downloadBtn.style.display = 'inline-block';
    } else {
        resultMessage.textContent = status.message || '수집된 데이터가 없습니다.';
        downloadBtn.style.display = 'none';
    }
}

// 다운로드 버튼
downloadBtn.addEventListener('click', () => {
    if (resultFilePath) {
        const filename = resultFilePath.split('/').pop().split('\\').pop();
        window.location.href = `/api/download/${filename}`;
    }
});

// 파일 목록 로드
async function loadFilesList() {
    try {
        filesList.innerHTML = '<p class="loading">파일 목록을 불러오는 중...</p>';

        const response = await fetch('/api/files');
        const data = await response.json();

        if (data.files && data.files.length > 0) {
            renderFilesList(data.files);
        } else {
            filesList.innerHTML = '<p class="empty">저장된 파일이 없습니다.</p>';
        }
    } catch (error) {
        filesList.innerHTML = '<p class="empty">파일 목록을 불러오는 중 오류가 발생했습니다.</p>';
        console.error('파일 목록 로드 오류:', error);
    }
}

// 파일 목록 렌더링
function renderFilesList(files) {
    filesList.innerHTML = '';

    files.forEach(file => {
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item';

        const sizeKB = (file.size / 1024).toFixed(2);

        fileItem.innerHTML = `
            <div class="file-info">
                <div class="file-name">${file.name}</div>
                <div class="file-meta">${sizeKB} KB · ${file.modified}</div>
            </div>
            <div class="file-actions">
                <a href="/api/download/${file.name}" download>다운로드</a>
            </div>
        `;

        filesList.appendChild(fileItem);
    });
}

// 파일 목록 새로고침 버튼
refreshFilesBtn.addEventListener('click', () => {
    loadFilesList();
});

// 폼 필드 변경 시 날짜 범위 예상 건수 표시 (선택사항)
document.querySelectorAll('input[name="mode"]').forEach(radio => {
    radio.addEventListener('change', updateEstimatedCount);
});

document.getElementById('start_date').addEventListener('change', updateEstimatedCount);
document.getElementById('end_date').addEventListener('change', updateEstimatedCount);

function updateEstimatedCount() {
    const startDate = document.getElementById('start_date').value;
    const endDate = document.getElementById('end_date').value;
    const mode = document.querySelector('input[name="mode"]:checked').value;

    if (!startDate || !endDate) return;

    const start = new Date(startDate);
    const end = new Date(endDate);

    if (start > end) return;

    let count = 0;
    const diffDays = Math.ceil((end - start) / (1000 * 60 * 60 * 24)) + 1;

    if (mode === 'daily') {
        count = diffDays;
    } else if (mode === 'weekly') {
        count = Math.ceil(diffDays / 7);
    } else if (mode === 'monthly') {
        // 대략적인 월 수 계산
        const months = (end.getFullYear() - start.getFullYear()) * 12 +
                      (end.getMonth() - start.getMonth()) + 1;
        count = months;
    }

    // 예상 건수를 상태 메시지로 표시 (선택사항)
    console.log(`예상 크롤링 횟수: ${count}회`);
}

// 초기 예상 건수 계산
updateEstimatedCount();
