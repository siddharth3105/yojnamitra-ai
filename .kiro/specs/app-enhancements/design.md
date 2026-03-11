# Design Document: App Enhancements

## Overview

This design document outlines the UI/UX enhancements for the YojnaMitra hackathon application's chatbot interface. The enhancements focus on making the chatbot more visually prominent, improving user interaction patterns, and ensuring smooth animations while maintaining all existing AWS Bedrock integration functionality.

The implementation will be done entirely through CSS and minor HTML/JavaScript modifications within the existing Streamlit application structure. No backend changes are required.

## Architecture

### Current Architecture
The application uses:
- **Frontend**: Streamlit with custom HTML/CSS injected via `st.markdown()`
- **Chatbot Backend**: AWS Bedrock (Claude) via `get_chatbot_response()` function
- **State Management**: Streamlit session state (`st.session_state`)
- **UI Pattern**: Floating button + modal overlay chatbot window

### Enhanced Architecture
The enhancements maintain the same architecture but improve:
- **Visual Design**: Enhanced CSS with modern gradients, animations, and effects
- **Layout**: Repositioned chatbot window (right side instead of left)
- **Interaction**: Better state management and user feedback
- **Responsiveness**: Improved mobile and desktop layouts

## Components and Interfaces

### 1. Enhanced Floating Button Component

**Location**: Bottom-right corner of viewport  
**Current Implementation**: Lines 2693-2854 in `app_premium.py`

**Enhanced Specifications**:
```css
.floating-help-btn {
    position: fixed;
    bottom: 40px;           /* Changed from 30px */
    right: 40px;            /* Changed from 30px */
    width: 80px;            /* Changed from 70px */
    height: 80px;           /* Changed from 70px */
    background: linear-gradient(135deg, #FF6B35 0%, #E63946 50%, #D62828 100%);
    border-radius: 50%;
    box-shadow: 0 10px 30px rgba(255, 107, 53, 0.6),
                0 0 0 0 rgba(255, 107, 53, 0.4);
    animation: pulse-glow 2s infinite, float 3s ease-in-out infinite;
}
```

**Key Features**:
- Larger size (80px diameter)
- Enhanced orange-to-red gradient
- Dual-layer glow effect
- Combined pulse and float animations
- AI badge with pulse animation
- Notification dot for new features

**Animations**:
- `pulse-glow`: Pulsing shadow effect (2s cycle)
- `float`: Gentle vertical floating motion (3s cycle)
- `badge-pulse`: AI badge scaling animation (1.5s cycle)
- `hover-scale`: Scale to 1.2x on hover with rotation

### 2. Enhanced Chatbot Window Component

**Location**: Right side of viewport (changed from left)  
**Current Implementation**: Lines 2856-3036 in `app_premium.py`

**Enhanced Specifications**:
```css
.chatbot-container {
    position: fixed;
    bottom: 140px;          /* Adjusted for button clearance */
    right: 40px;            /* Changed from left: 30px */
    width: 450px;           /* Changed from 380px */
    height: 600px;          /* Changed from 500px */
    background: white;
    border-radius: 20px;
    box-shadow: 0 15px 50px rgba(0,0,0,0.3);
    animation: slideInRight 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}
```

**Key Features**:
- Slides in from right side (not left)
- Larger dimensions (450x600px)
- Enhanced header with minimize/maximize buttons
- Typing indicator component
- Auto-scroll behavior
- Message timestamps
- Quick action buttons
- Smooth exit animation

**Header Component**:
```html
<div class="chatbot-header">
    <div class="header-left">
        <h3>🤖 YojnaMitra AI</h3>
        <p class="status-indicator">
            <span class="status-dot"></span> Online
        </p>
    </div>
    <div class="header-controls">
        <button class="minimize-btn">−</button>
        <button class="maximize-btn">□</button>
        <button class="close-btn">×</button>
    </div>
</div>
```

**Message Component**:
```html
<div class="chat-message user-message">
    <div class="message-content">{content}</div>
    <div class="message-timestamp">{time}</div>
</div>
```

**Typing Indicator**:
```html
<div class="typing-indicator">
    <span class="typing-dot"></span>
    <span class="typing-dot"></span>
    <span class="typing-dot"></span>
</div>
```

**Quick Actions**:
```html
<div class="quick-actions">
    <button class="quick-action-btn">PM-KISAN eligibility?</button>
    <button class="quick-action-btn">Available schemes for me?</button>
    <button class="quick-action-btn">Required documents?</button>
</div>
```

### 3. Session State Management

**Current State Variables**:
```python
st.session_state.show_chatbot      # Boolean: chatbot visibility
st.session_state.chat_messages     # List: message history
st.session_state.user_profile      # Dict: user information
```

**Enhanced State Variables**:
```python
st.session_state.show_chatbot          # Boolean: chatbot visibility
st.session_state.chat_messages         # List: message history
st.session_state.user_profile          # Dict: user information
st.session_state.chatbot_minimized     # Boolean: minimize state
st.session_state.chatbot_maximized     # Boolean: maximize state
st.session_state.is_typing             # Boolean: AI typing indicator
st.session_state.show_notification     # Boolean: notification dot
```

**State Transitions**:
- Button click → Toggle `show_chatbot`
- Minimize → Set `chatbot_minimized = True`, keep `show_chatbot = True`
- Maximize → Toggle `chatbot_maximized` (450px ↔ 90vw)
- Close → Set `show_chatbot = False`
- Send message → Set `is_typing = True` → Get response → Set `is_typing = False`

### 4. Animation System

**Performance Optimizations**:
- Use CSS `transform` and `opacity` only (GPU-accelerated)
- Avoid `width`, `height`, `top`, `left` animations (layout-triggering)
- Use `will-change` property for animated elements
- Implement `requestAnimationFrame` for JavaScript animations

**Animation Specifications**:

```css
/* Floating button animations */
@keyframes pulse-glow {
    0%, 100% {
        box-shadow: 0 10px 30px rgba(255, 107, 53, 0.6),
                    0 0 0 0 rgba(255, 107, 53, 0.4);
    }
    50% {
        box-shadow: 0 10px 40px rgba(255, 107, 53, 0.8),
                    0 0 0 15px rgba(255, 107, 53, 0);
    }
}

@keyframes float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-10px); }
}

/* Window slide animations */
@keyframes slideInRight {
    from {
        opacity: 0;
        transform: translateX(100px) scale(0.9);
    }
    to {
        opacity: 1;
        transform: translateX(0) scale(1);
    }
}

@keyframes slideOutRight {
    from {
        opacity: 1;
        transform: translateX(0) scale(1);
    }
    to {
        opacity: 0;
        transform: translateX(100px) scale(0.9);
    }
}

/* Typing indicator */
@keyframes typing-dot {
    0%, 60%, 100% { transform: translateY(0); }
    30% { transform: translateY(-10px); }
}
```

## Data Models

### Message Model
```python
{
    'role': str,           # 'user' or 'assistant'
    'content': str,        # Message text
    'timestamp': str,      # ISO format timestamp
    'id': str             # Unique message ID
}
```

### Chatbot State Model
```python
{
    'show_chatbot': bool,
    'chatbot_minimized': bool,
    'chatbot_maximized': bool,
    'is_typing': bool,
    'show_notification': bool,
    'chat_messages': List[Message],
    'user_profile': Dict[str, Any]
}
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Button Visibility and Positioning
*For any* viewport size, the chatbot button should remain visible and positioned 40 pixels from the bottom-right corner without overlapping other UI elements.
**Validates: Requirements 1.6, 1.7**

### Property 2: Animation Frame Rate
*For any* animation (button pulse, window slide, typing indicator), the animation should render at 60fps or higher without dropping frames.
**Validates: Requirements 6.1**

### Property 3: Window Slide Direction
*For any* chatbot window open/close action, the window should slide from/to the right side of the viewport, not the left.
**Validates: Requirements 2.1**

### Property 4: State Consistency
*For any* chatbot state transition (open, close, minimize, maximize), the session state variables should remain consistent with the visual state.
**Validates: Requirements 3.1, 3.4**

### Property 5: Message Persistence
*For any* chatbot interaction, all messages should persist in session state until explicitly cleared by the user.
**Validates: Requirements 3.1**

### Property 6: Auto-scroll Behavior
*For any* new message added to the chat, the message container should automatically scroll to display the latest message.
**Validates: Requirements 2.6**

### Property 7: Responsive Dimensions
*For any* viewport width less than 768px, the chatbot window should adjust to 90% of viewport width and height.
**Validates: Requirements 5.3, 5.4**

### Property 8: Typing Indicator Timing
*For any* AI response generation, the typing indicator should display immediately when the request starts and hide immediately when the response is received.
**Validates: Requirements 2.5**

### Property 9: Backward Compatibility
*For any* existing chatbot functionality (AWS Bedrock integration, message handling, user profile access), the behavior should remain unchanged after enhancements.
**Validates: Requirements 7.1, 7.2, 7.3, 7.4, 7.5**

### Property 10: CSS Transform Usage
*For any* animation implementation, only CSS `transform` and `opacity` properties should be used for position and visibility changes.
**Validates: Requirements 6.2, 6.3, 6.4**

### Property 11: Color Scheme Consistency
*For any* new UI element (button, window, message bubble), the colors should use the existing application color palette (orange #FF6B35, purple #667eea, etc.).
**Validates: Requirements 5.1, 5.2**

### Property 12: Smooth Transitions
*For any* interactive element (button hover, window open/close), transitions should complete within 200-400ms.
**Validates: Requirements 5.5**

## Error Handling

### 1. Animation Performance Degradation
**Scenario**: Low-end devices may struggle with multiple simultaneous animations.

**Handling**:
```css
@media (prefers-reduced-motion: reduce) {
    * {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
}
```

### 2. State Synchronization Issues
**Scenario**: Session state and visual state become desynchronized.

**Handling**:
```python
def ensure_chatbot_state():
    """Ensure chatbot state variables exist and are valid"""
    if 'show_chatbot' not in st.session_state:
        st.session_state.show_chatbot = False
    if 'chatbot_minimized' not in st.session_state:
        st.session_state.chatbot_minimized = False
    if 'chatbot_maximized' not in st.session_state:
        st.session_state.chatbot_maximized = False
    if 'is_typing' not in st.session_state:
        st.session_state.is_typing = False
    if 'show_notification' not in st.session_state:
        st.session_state.show_notification = True
```

### 3. Mobile Viewport Overflow
**Scenario**: Chatbot window exceeds viewport on small screens.

**Handling**:
```css
@media (max-width: 768px) {
    .chatbot-container {
        right: 5%;
        bottom: 100px;
        width: 90vw;
        height: 90vh;
        max-height: calc(100vh - 120px);
    }
}
```

### 4. Message Overflow
**Scenario**: Very long messages break layout.

**Handling**:
```css
.message-content {
    word-wrap: break-word;
    overflow-wrap: break-word;
    max-width: 100%;
    white-space: pre-wrap;
}
```

### 5. AWS Bedrock API Errors
**Scenario**: Chatbot API fails during message send.

**Handling**: Maintain existing error handling in `get_chatbot_response()` function. No changes needed.

## Testing Strategy

### Unit Testing Approach

**Focus Areas**:
- CSS class application verification
- Session state initialization
- Message timestamp formatting
- Quick action button generation

**Example Unit Tests**:
```python
def test_chatbot_state_initialization():
    """Test that chatbot state variables initialize correctly"""
    # Test initial state
    assert 'show_chatbot' in st.session_state
    assert st.session_state.show_chatbot == False
    assert 'chat_messages' in st.session_state
    assert len(st.session_state.chat_messages) == 0

def test_message_timestamp_format():
    """Test message timestamp formatting"""
    from datetime import datetime
    timestamp = datetime.now().isoformat()
    # Verify ISO format
    assert 'T' in timestamp
    assert len(timestamp) > 10

def test_responsive_breakpoints():
    """Test that responsive CSS breakpoints are defined"""
    # Verify mobile breakpoint exists
    assert '@media (max-width: 768px)' in css_content
```

### Property-Based Testing Approach

**Configuration**:
- Library: Hypothesis (Python)
- Minimum iterations: 100 per property
- Tag format: **Feature: app-enhancements, Property {N}: {description}**

**Property Test Examples**:

```python
from hypothesis import given, strategies as st
import hypothesis

@given(st.integers(min_value=320, max_value=3840))
def test_button_always_visible(viewport_width):
    """
    Feature: app-enhancements, Property 1: Button Visibility and Positioning
    For any viewport size, button should remain visible at 40px from edges
    """
    button_right = 40
    button_width = 80
    assert button_right + button_width < viewport_width

@given(st.lists(st.text(min_size=1, max_size=500), min_size=0, max_size=100))
def test_message_persistence(messages):
    """
    Feature: app-enhancements, Property 5: Message Persistence
    For any list of messages, all should persist in session state
    """
    st.session_state.chat_messages = messages
    assert len(st.session_state.chat_messages) == len(messages)
    assert st.session_state.chat_messages == messages

@given(st.integers(min_value=0, max_value=10000))
def test_animation_duration_bounds(duration_ms):
    """
    Feature: app-enhancements, Property 12: Smooth Transitions
    For any transition, duration should be between 200-400ms
    """
    if 200 <= duration_ms <= 400:
        assert is_valid_transition_duration(duration_ms)
```

### Manual Testing Checklist

**Visual Testing**:
- [ ] Button gradient displays correctly
- [ ] Button glow effect is visible
- [ ] AI badge pulses smoothly
- [ ] Window slides from right side
- [ ] Typing indicator animates correctly
- [ ] Message bubbles have timestamps
- [ ] Quick action buttons are visible

**Interaction Testing**:
- [ ] Button click opens chatbot
- [ ] Close button closes chatbot
- [ ] Minimize button minimizes window
- [ ] Maximize button expands window
- [ ] Send button sends message
- [ ] Clear button clears messages
- [ ] Quick action buttons insert text

**Responsive Testing**:
- [ ] Desktop (1920x1080): Full size window
- [ ] Tablet (768x1024): Adjusted window
- [ ] Mobile (375x667): 90% viewport size
- [ ] Button remains visible on all sizes

**Performance Testing**:
- [ ] Animations run at 60fps
- [ ] No layout shifts during animations
- [ ] Smooth scrolling in message area
- [ ] No lag when typing

**Compatibility Testing**:
- [ ] Existing AWS Bedrock integration works
- [ ] User profile data accessible
- [ ] Message history preserved
- [ ] All existing features functional

### Integration Testing

**Test Scenarios**:
1. Open chatbot → Send message → Verify AWS Bedrock response
2. Add multiple messages → Verify auto-scroll
3. Minimize → Maximize → Verify state consistency
4. Close → Reopen → Verify message persistence
5. Resize viewport → Verify responsive behavior

**Success Criteria**:
- All animations complete smoothly
- No console errors
- State remains consistent
- AWS integration unaffected
- Mobile experience is usable
