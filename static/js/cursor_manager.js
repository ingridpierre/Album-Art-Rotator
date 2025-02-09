class CursorManager {
    constructor(timeout = 3000) {
        this.timeout = timeout;
        this.timeoutId = null;
        this.isHidden = false;
        this.init();
    }

    init() {
        // Reset timer on any mouse movement
        document.addEventListener('mousemove', () => this.showCursor());
        // Initial cursor check
        this.startTimer();
    }

    showCursor() {
        document.body.classList.remove('cursor-hidden');
        this.isHidden = false;
        this.startTimer();
    }

    hideCursor() {
        document.body.classList.add('cursor-hidden');
        this.isHidden = true;
    }

    startTimer() {
        if (this.timeoutId) {
            clearTimeout(this.timeoutId);
        }
        this.timeoutId = setTimeout(() => this.hideCursor(), this.timeout);
    }
}

// Initialize cursor manager when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new CursorManager(3000); // 3 seconds timeout
});
