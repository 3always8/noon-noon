import cv2
from typing import Optional, Tuple
from .model import NoonState

try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False


class EyeTracker:
    """
    웹캠을 사용하여 얼굴 및 눈의 움직임을 추적하고 NoonState의 gaze 값을 업데이트합니다.
    MediaPipe가 있으면 Face Mesh를 사용하고, 없으면 OpenCV Haar Cascades를 사용합니다.
    """
    
    def __init__(self, camera_index: int = 0, smoothing_factor: float = 0.7, use_mediapipe: bool = True, show_preview: bool = True):
        """
        Args:
            camera_index: 웹캠 인덱스 (기본값: 0)
            smoothing_factor: 이동 평균 스무딩 계수 (0.0~1.0, 높을수록 부드러움)
            use_mediapipe: MediaPipe 사용 여부 (없으면 OpenCV Haar Cascades 사용)
            show_preview: 웹캠 미리보기 창 표시 여부
        """
        self.camera_index = camera_index
        self.smoothing_factor = smoothing_factor
        self.use_mediapipe = use_mediapipe and MEDIAPIPE_AVAILABLE
        self.show_preview = show_preview
        self.cap: Optional[cv2.VideoCapture] = None
        
        # 얼굴/눈 위치 정보 (렌더링용)
        self.face_rect: Optional[Tuple[int, int, int, int]] = None  # (x, y, w, h)
        self.left_eye_pos: Optional[Tuple[int, int]] = None  # (cx, cy)
        self.right_eye_pos: Optional[Tuple[int, int]] = None  # (cx, cy)
        self.eye_size: Optional[float] = None  # 눈 크기 추정
        
        if self.use_mediapipe:
            # MediaPipe 초기화
            self.mp_face_mesh = mp.solutions.face_mesh
            self.face_mesh = self.mp_face_mesh.FaceMesh(
                max_num_faces=1,
                refine_landmarks=True,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
            # 눈 랜드마크 인덱스
            self.LEFT_EYE_INDICES = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
            self.RIGHT_EYE_INDICES = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
        else:
            # OpenCV Haar Cascades 초기화
            try:
                self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
                self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
            except Exception as e:
                raise RuntimeError(f"Failed to load Haar Cascades: {e}")
        
        # 스무딩을 위한 이전 값들
        self.prev_gaze_x = 0.0
        self.prev_gaze_y = 0.0
        self.gaze_velocity_x = 0.0
        self.gaze_velocity_y = 0.0
        
        # 얼굴 중심점 (정규화된 좌표)
        self.face_center_x = 0.5
        self.face_center_y = 0.5
        self.face_velocity_x = 0.0
        self.face_velocity_y = 0.0
        
        # 얼굴 크기 추적 (정규화된 값, 0.0~1.0)
        self.face_size_normalized = 0.5  # 기본값
        self.prev_face_size = 0.5
        self.face_size_velocity = 0.0
        
        # 얼굴 크기 범위 설정 (화면 대비 최소/최대 비율)
        self.min_face_ratio = 0.1   # 화면의 10% (멀리 있을 때)
        self.max_face_ratio = 0.5   # 화면의 50% (가까이 있을 때)
        
        # ring_inner_ratio 변화 속도 (낮을수록 부드러움)
        self.ring_ratio_smoothing = 0.1
        
        # 적응형 스무딩을 위한 변수
        self.adaptive_smoothing_factor = smoothing_factor
        self.movement_threshold = 0.02  # 움직임 감지 임계값
        self.fast_movement_factor = 0.5  # 빠른 움직임일 때 스무딩 감소
        self.slow_movement_factor = 0.9  # 느린 움직임일 때 스무딩 증가
        
        # 얼굴 손실 추적
        self.face_lost_frames = 0
        self.max_lost_frames = 10  # 얼굴이 감지되지 않을 때 유지할 프레임 수
        
    def start(self) -> bool:
        """웹캠을 시작합니다."""
        self.cap = cv2.VideoCapture(self.camera_index)
        if not self.cap.isOpened():
            return False
        # 프레임 속도 설정 (Raspberry Pi 최적화)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        return True
    
    def stop(self):
        """웹캠을 중지하고 리소스를 해제합니다."""
        if self.cap:
            self.cap.release()
            self.cap = None
        if self.use_mediapipe:
            self.face_mesh.close()
        if self.show_preview:
            cv2.destroyAllWindows()
    
    def _get_eye_center_mediapipe(self, landmarks, eye_indices, img_width: int, img_height: int) -> Tuple[Optional[float], Optional[float]]:
        """MediaPipe를 사용하여 눈의 중심점을 계산합니다."""
        eye_points = []
        for idx in eye_indices:
            landmark = landmarks.landmark[idx]
            x = int(landmark.x * img_width)
            y = int(landmark.y * img_height)
            eye_points.append((x, y))
        
        if not eye_points:
            return None, None
        
        cx = sum(p[0] for p in eye_points) / len(eye_points)
        cy = sum(p[1] for p in eye_points) / len(eye_points)
        return cx, cy
    
    def _get_face_center_opencv(self, frame) -> Tuple[Optional[float], Optional[float]]:
        """OpenCV Haar Cascades를 사용하여 얼굴 중심점을 계산합니다."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
        
        if len(faces) == 0:
            self.face_rect = None
            return None, None
        
        # 첫 번째 얼굴만 사용
        x, y, w, h = faces[0]
        self.face_rect = (x, y, w, h)
        
        # 눈 감지 (얼굴 영역 내에서)
        roi_gray = gray[y:y+h, x:x+w]
        eyes = self.eye_cascade.detectMultiScale(roi_gray, 1.1, 3)
        
        if len(eyes) >= 2:
            # 두 눈의 위치 계산
            eyes_sorted = sorted(eyes, key=lambda e: e[0])  # x 좌표로 정렬
            left_eye = eyes_sorted[0]
            right_eye = eyes_sorted[1]
            
            left_eye_cx = x + left_eye[0] + left_eye[2] // 2
            left_eye_cy = y + left_eye[1] + left_eye[3] // 2
            right_eye_cx = x + right_eye[0] + right_eye[2] // 2
            right_eye_cy = y + right_eye[1] + right_eye[3] // 2
            
            self.left_eye_pos = (left_eye_cx, left_eye_cy)
            self.right_eye_pos = (right_eye_cx, right_eye_cy)
            self.eye_size = (left_eye[2] + left_eye[3] + right_eye[2] + right_eye[3]) / 4.0
        else:
            # 눈이 감지되지 않으면 얼굴 크기로 추정
            eye_spacing = w * 0.3
            self.left_eye_pos = (x + w // 2 - int(eye_spacing), y + h // 3)
            self.right_eye_pos = (x + w // 2 + int(eye_spacing), y + h // 3)
            self.eye_size = w * 0.15
        
        # 얼굴 중심점 계산
        face_center_x = (x + w / 2) / frame.shape[1]
        face_center_y = (y + h / 2) / frame.shape[0]
        
        return face_center_x, face_center_y
    
    def _calculate_gaze_from_head_position(self, face_center_x: float, face_center_y: float) -> Tuple[float, float]:
        """
        얼굴의 위치를 기반으로 gaze 값을 계산합니다.
        얼굴이 화면 중앙에서 벗어난 정도를 gaze 값으로 변환합니다.
        """
        # 얼굴 중심이 화면 중앙(0.5, 0.5)에서 얼마나 벗어났는지 계산
        # -1.0 ~ 1.0 범위로 정규화
        gaze_x = (face_center_x - 0.5) * 2.0  # -1.0(왼쪽) ~ 1.0(오른쪽)
        gaze_y = (face_center_y - 0.5) * 2.0  # -1.0(위) ~ 1.0(아래)
        
        # 범위 제한
        gaze_x = max(-1.0, min(1.0, gaze_x))
        gaze_y = max(-1.0, min(1.0, gaze_y))
        
        return gaze_x, gaze_y
    
    def update(self, state: NoonState) -> bool:
        """
        웹캠에서 프레임을 읽고 얼굴을 감지하여 state의 gaze 값을 업데이트합니다.
        
        Args:
            state: 업데이트할 NoonState 객체
            
        Returns:
            얼굴이 감지되었으면 True, 그렇지 않으면 False
        """
        if not self.cap or not self.cap.isOpened():
            return False
        
        ret, frame = self.cap.read()
        if not ret:
            return False
        
        img_height, img_width = frame.shape[:2]
        face_center_x = None
        face_center_y = None
        
        if self.use_mediapipe:
            # MediaPipe 사용
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.face_mesh.process(rgb_frame)
            
            if results.multi_face_landmarks:
                face_landmarks = results.multi_face_landmarks[0]
                
                # 왼쪽 눈과 오른쪽 눈의 중심점 계산
                left_eye_cx, left_eye_cy = self._get_eye_center_mediapipe(
                    face_landmarks, self.LEFT_EYE_INDICES, img_width, img_height
                )
                right_eye_cx, right_eye_cy = self._get_eye_center_mediapipe(
                    face_landmarks, self.RIGHT_EYE_INDICES, img_width, img_height
                )
                
                if left_eye_cx is not None and right_eye_cx is not None:
                    # 눈 위치 저장 (렌더링용)
                    self.left_eye_pos = (int(left_eye_cx), int(left_eye_cy))
                    self.right_eye_pos = (int(right_eye_cx), int(right_eye_cy))
                    
                    # 눈 크기 추정 (랜드마크 간 거리 기반)
                    eye_width = abs(right_eye_cx - left_eye_cx)
                    self.eye_size = eye_width * 0.15
                    
                    # 얼굴 영역 추정
                    face_bbox = self._get_face_bbox_mediapipe(face_landmarks, img_width, img_height)
                    if face_bbox:
                        self.face_rect = face_bbox
                    
                    # 두 눈의 중점을 얼굴 중심으로 사용
                    face_center_x = (left_eye_cx + right_eye_cx) / 2.0 / img_width
                    face_center_y = (left_eye_cy + right_eye_cy) / 2.0 / img_height
        else:
            # OpenCV Haar Cascades 사용
            face_center_x, face_center_y = self._get_face_center_opencv(frame)
        
        if face_center_x is None or face_center_y is None:
            # 얼굴이 감지되지 않으면 프레임 카운터 증가
            self.face_lost_frames += 1
            
            # 얼굴이 일정 시간 동안 감지되지 않으면 부드럽게 기본값으로 복귀
            if self.face_lost_frames > self.max_lost_frames:
                # 속도 감쇠
                self.face_velocity_x *= 0.9
                self.face_velocity_y *= 0.9
                self.gaze_velocity_x *= 0.9
                self.gaze_velocity_y *= 0.9
                
                # 기본값으로 부드럽게 복귀
                self.face_center_x = 0.5 + (self.face_center_x - 0.5) * 0.95
                self.face_center_y = 0.5 + (self.face_center_y - 0.5) * 0.95
                
                # Gaze 값도 중앙으로 복귀
                gaze_x = (self.prev_gaze_x * 0.95)
                gaze_y = (self.prev_gaze_y * 0.95)
                state.gaze_x = gaze_x
                state.gaze_y = gaze_y
                self.prev_gaze_x = gaze_x
                self.prev_gaze_y = gaze_y
                
                self.face_size_normalized = 0.5 + (self.face_size_normalized - 0.5) * 0.95
                self._update_ring_inner_ratio(state, img_width, img_height)
            
            self.face_rect = None
            self.left_eye_pos = None
            self.right_eye_pos = None
            
            if self.show_preview:
                self._draw_tracking_rectangle(frame)
                cv2.imshow('User Face', frame)
                cv2.waitKey(1)
            return False
        
        # 얼굴이 감지되면 프레임 카운터 리셋
        self.face_lost_frames = 0
        
        # 얼굴 중심 위치를 적응형 스무딩으로 업데이트
        face_delta_x = face_center_x - self.face_center_x
        face_delta_y = face_center_y - self.face_center_y
        face_movement = abs(face_delta_x) + abs(face_delta_y)
        
        # 움직임 속도에 따라 적응형 스무딩 적용
        if face_movement > self.movement_threshold:
            # 빠른 움직임: 더 빠른 반응
            adaptive_factor = self.fast_movement_factor
        else:
            # 느린 움직임: 더 부드러운 스무딩
            adaptive_factor = self.slow_movement_factor
        
        # 속도 기반 예측 (간단한 물리 시뮬레이션)
        self.face_velocity_x = self.face_velocity_x * 0.7 + face_delta_x * 0.3
        self.face_velocity_y = self.face_velocity_y * 0.7 + face_delta_y * 0.3
        
        # 예측된 위치로 스무딩 (속도 고려)
        predicted_x = face_center_x + self.face_velocity_x * 0.3
        predicted_y = face_center_y + self.face_velocity_y * 0.3
        
        self.face_center_x = (
            adaptive_factor * self.face_center_x + 
            (1 - adaptive_factor) * predicted_x
        )
        self.face_center_y = (
            adaptive_factor * self.face_center_y + 
            (1 - adaptive_factor) * predicted_y
        )
        
        # gaze 값 계산
        gaze_x, gaze_y = self._calculate_gaze_from_head_position(
            self.face_center_x, self.face_center_y
        )
        
        # Gaze 값 적응형 스무딩
        gaze_delta_x = gaze_x - self.prev_gaze_x
        gaze_delta_y = gaze_y - self.prev_gaze_y
        gaze_movement = abs(gaze_delta_x) + abs(gaze_delta_y)
        
        if gaze_movement > self.movement_threshold:
            adaptive_gaze_factor = self.fast_movement_factor
        else:
            adaptive_gaze_factor = self.slow_movement_factor
        
        # Gaze 속도 추적
        self.gaze_velocity_x = self.gaze_velocity_x * 0.7 + gaze_delta_x * 0.3
        self.gaze_velocity_y = self.gaze_velocity_y * 0.7 + gaze_delta_y * 0.3
        
        # 예측된 gaze 값
        predicted_gaze_x = gaze_x + self.gaze_velocity_x * 0.2
        predicted_gaze_y = gaze_y + self.gaze_velocity_y * 0.2
        
        gaze_x = (
            adaptive_gaze_factor * self.prev_gaze_x + 
            (1 - adaptive_gaze_factor) * predicted_gaze_x
        )
        gaze_y = (
            adaptive_gaze_factor * self.prev_gaze_y + 
            (1 - adaptive_gaze_factor) * predicted_gaze_y
        )
        
        # 상태 업데이트
        state.gaze_x = gaze_x
        state.gaze_y = gaze_y
        
        # 얼굴 크기 기반으로 ring_inner_ratio 업데이트
        self._update_ring_inner_ratio(state, img_width, img_height)
        
        # 이전 값 저장
        self.prev_gaze_x = gaze_x
        self.prev_gaze_y = gaze_y
        
        # 미리보기 창에 그리기
        if self.show_preview:
            self._draw_tracking_rectangle(frame)
            cv2.imshow('User Face', frame)
            cv2.waitKey(1)
        
        return True
    
    def _get_face_bbox_mediapipe(self, landmarks, img_width: int, img_height: int) -> Optional[Tuple[int, int, int, int]]:
        """MediaPipe 랜드마크로부터 얼굴 바운딩 박스를 계산합니다."""
        xs = [landmark.x * img_width for landmark in landmarks.landmark]
        ys = [landmark.y * img_height for landmark in landmarks.landmark]
        
        if not xs or not ys:
            return None
        
        x_min, x_max = int(min(xs)), int(max(xs))
        y_min, y_max = int(min(ys)), int(max(ys))
        w = x_max - x_min
        h = y_max - y_min
        
        return (x_min, y_min, w, h)
    
    def _update_ring_inner_ratio(self, state: NoonState, img_width: int, img_height: int):
        """
        얼굴 크기에 따라 ring_inner_ratio를 부드럽게 업데이트합니다.
        얼굴이 가까이 있으면(큰 사각형) inner hole이 커지고,
        멀리 있으면(작은 사각형) inner hole이 작아집니다.
        """
        if self.face_rect:
            x, y, w, h = self.face_rect
            # 얼굴 크기 계산 (면적 기준)
            face_area = w * h
            screen_area = img_width * img_height
            face_ratio = face_area / screen_area if screen_area > 0 else 0.0
            
            # 정규화 (min_face_ratio ~ max_face_ratio 범위를 0.0 ~ 1.0으로)
            if face_ratio < self.min_face_ratio:
                normalized_size = 0.0
            elif face_ratio > self.max_face_ratio:
                normalized_size = 1.0
            else:
                normalized_size = (face_ratio - self.min_face_ratio) / (self.max_face_ratio - self.min_face_ratio)
            
            # 얼굴 크기 변화량 계산
            size_delta = normalized_size - self.face_size_normalized
            size_movement = abs(size_delta)
            
            # 적응형 스무딩
            if size_movement > 0.05:
                size_factor = self.fast_movement_factor
            else:
                size_factor = self.slow_movement_factor
            
            # 속도 추적
            self.face_size_velocity = self.face_size_velocity * 0.7 + size_delta * 0.3
            
            # 예측된 크기
            predicted_size = normalized_size + self.face_size_velocity * 0.2
            
            # 스무딩 적용
            self.face_size_normalized = (
                size_factor * self.face_size_normalized +
                (1 - size_factor) * predicted_size
            )
        else:
            # 얼굴이 없으면 기본값(0.5)으로 부드럽게 복귀
            self.face_size_normalized = (
                self.smoothing_factor * self.face_size_normalized +
                (1 - self.smoothing_factor) * 0.5
            )
        
        # ring_inner_ratio 범위 설정 (0.5 ~ 0.85)
        # 얼굴이 가까이 있으면(1.0) -> 0.85 (큰 구멍)
        # 얼굴이 멀리 있으면(0.0) -> 0.5 (작은 구멍)
        target_ratio = 0.5 + (self.face_size_normalized * 0.35)
        
        # 부드러운 전환 적용
        current_ratio = state.ring_inner_ratio
        new_ratio = current_ratio + (target_ratio - current_ratio) * self.ring_ratio_smoothing
        
        # 범위 제한 (0.0 ~ 1.0)
        state.ring_inner_ratio = max(0.0, min(1.0, new_ratio))
    
    def _draw_tracking_rectangle(self, frame):
        """웹캠 프레임에 얼굴 추적 영역을 사각형으로 표시합니다."""
        if self.face_rect:
            x, y, w, h = self.face_rect
            # 추적 영역 사각형 그리기 (녹색)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # 눈 위치 표시 (선택사항)
            if self.left_eye_pos and self.right_eye_pos:
                cv2.circle(frame, self.left_eye_pos, 5, (0, 255, 0), -1)
                cv2.circle(frame, self.right_eye_pos, 5, (0, 255, 0), -1)
    
    def __enter__(self):
        """Context manager 진입"""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager 종료"""
        self.stop()

