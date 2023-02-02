package kongsang.swybot;

import android.annotation.SuppressLint;
import android.content.Context;
import android.graphics.PixelFormat;
import android.os.Build;
import android.view.Gravity;
import android.view.MotionEvent;
import android.view.View;
import android.view.WindowManager;
import android.widget.ImageView;

public class FloatingButtonWindow implements View.OnTouchListener {
    private final WindowManager windowManager;
    private final WindowManager.LayoutParams layoutParams;
    private final ImageView imageView;
    private View.OnClickListener listener;
    private int x;
    private int y;
    private boolean isMoving;

    @SuppressLint("ClickableViewAccessibility")
    public FloatingButtonWindow(Context context) {
        windowManager = (WindowManager) context.getSystemService(Context.WINDOW_SERVICE);

        int length = SystemUtil.dip2px(context, 48);
        layoutParams = new WindowManager.LayoutParams();
        layoutParams.width = length;
        layoutParams.height = length;
        layoutParams.x = 0;
        layoutParams.y = SystemUtil.dip2px(context, 120);
        layoutParams.gravity = Gravity.TOP | Gravity.END;
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            layoutParams.type = WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY;
        } else {
            layoutParams.type = WindowManager.LayoutParams.TYPE_PHONE;
        }
        layoutParams.flags = WindowManager.LayoutParams.FLAG_NOT_TOUCH_MODAL
                | WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE
                | WindowManager.LayoutParams.FLAG_LAYOUT_IN_SCREEN
                | WindowManager.LayoutParams.FLAG_LAYOUT_INSET_DECOR;
        layoutParams.format = PixelFormat.RGBA_8888;
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
            layoutParams.layoutInDisplayCutoutMode = WindowManager.LayoutParams.LAYOUT_IN_DISPLAY_CUTOUT_MODE_SHORT_EDGES;
        }

        imageView = new ImageView(context);
        imageView.setImageResource(R.drawable.ic_flower_24);
        imageView.setBackgroundResource(R.drawable.shape_circle);
        imageView.setClickable(true);
        imageView.setOnTouchListener(this);
    }

    public void setImage(int resId) {
        imageView.setImageResource(resId);
    }

    public void setOnClickListener(View.OnClickListener listener) {
        this.listener = listener;
    }

    public void show() {
        windowManager.addView(imageView, layoutParams);
    }

    public void hide() {
        windowManager.removeView(imageView);
    }

    @SuppressLint("ClickableViewAccessibility")
    @Override
    public boolean onTouch(View v, MotionEvent event) {
        switch (event.getAction()) {
            case MotionEvent.ACTION_DOWN:
                x = (int) event.getRawX();
                y = (int) event.getRawY();
                isMoving = false;
                return true;
            case MotionEvent.ACTION_MOVE:
                int nowX = (int) event.getRawX();
                int nowY = (int) event.getRawY();
                int moveX = nowX - x;
                int moveY = nowY - y;
                if (Math.abs(moveX) > 0 || Math.abs(moveY) > 0) {
                    isMoving = true;
                    x = nowX;
                    y = nowY;
                    layoutParams.x -= moveX;
                    layoutParams.y += moveY;
                    windowManager.updateViewLayout(imageView, layoutParams);
                    return true;
                }
                break;
            case MotionEvent.ACTION_UP:
                if (!isMoving && listener != null) {
                    listener.onClick(v);
                    return true;
                }
                break;
        }
        return false;
    }
}
