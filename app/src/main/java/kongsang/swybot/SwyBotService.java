package kongsang.swybot;

import android.accessibilityservice.AccessibilityService;
import android.accessibilityservice.AccessibilityServiceInfo;
import android.accessibilityservice.GestureDescription;
import android.app.AlertDialog;
import android.app.Service;
import android.content.Context;
import android.content.DialogInterface;
import android.content.Intent;
import android.content.SharedPreferences;
import android.graphics.Path;
import android.graphics.PixelFormat;
import android.hardware.display.DisplayManager;
import android.hardware.display.VirtualDisplay;
import android.media.Image;
import android.media.ImageReader;
import android.media.projection.MediaProjection;
import android.media.projection.MediaProjectionManager;
import android.os.Build;
import android.os.Handler;
import android.util.DisplayMetrics;
import android.util.Log;
import android.view.Surface;
import android.view.WindowManager;
import android.view.accessibility.AccessibilityEvent;

import androidx.core.app.NotificationCompat;

import com.chaquo.python.PyException;

import java.nio.ByteBuffer;
import java.util.List;

public class SwyBotService extends AccessibilityService {
    public static final int NOTIFICATION_ID = 233;
    private static final String TAG = "SwyBotService";

    private WindowManager windowManager;
    private SharedPreferences preferences;
    private Handler handler;
    private FloatingButtonWindow floatingButton;

    private Runnable taskCallback;
    private Thread taskThread;
    private MediaProjection mediaProjection;
    private ImageReader imageReader;
    private VirtualDisplay virtualDisplay;

    @Override
    public void onCreate() {
        super.onCreate();
        ScriptBridge.setService(this);

        windowManager = (WindowManager) getSystemService(WINDOW_SERVICE);
        preferences = getSharedPreferences("preferences", Context.MODE_PRIVATE);
        handler = new Handler(getMainLooper());

        floatingButton = new FloatingButtonWindow(this);
        floatingButton.setOnClickListener(v -> {
            if (taskThread == null) {
                ScriptBridge.getMainModule().callAttr("androidmenu");
            } else {
                stopTask();
            }
        });
        floatingButton.show();
    }

    @Override
    protected void onServiceConnected() {
        Log.i(TAG, "Accessibility service connected");
        AccessibilityServiceInfo serviceInfo = getServiceInfo();
        serviceInfo.packageNames = new String[] { MainActivity.SWY_PACKAGE_NAME };
        setServiceInfo(serviceInfo);
    }

    @Override
    public void onAccessibilityEvent(AccessibilityEvent event) {}

    @Override
    public void onInterrupt() {}

    @Override
    public void onDestroy() {
        super.onDestroy();
        stopTask();
        ScriptBridge.setService(null);
        floatingButton.hide();
    }

    public int[] getScreenSize() {
        // getResources().getDisplayMetrics() 获得的宽高不包括状态栏和导航栏
        // TODO 如果以后 Android 多窗口流行则需要改为 WindowManager.getCurrentWindowMetrics()
        DisplayMetrics displayMetrics = new DisplayMetrics();
        windowManager.getDefaultDisplay().getRealMetrics(displayMetrics);
        int width = Math.max(displayMetrics.widthPixels, displayMetrics.heightPixels);
        int height = Math.min(displayMetrics.widthPixels, displayMetrics.heightPixels);
        int rotation = windowManager.getDefaultDisplay().getRotation();
        return rotation == Surface.ROTATION_90 || rotation == Surface.ROTATION_270 ?
                new int[] { width, height } : new int[] { height, width };
    }

    public int getScreenDpi() {
        return getResources().getDisplayMetrics().densityDpi;
    }

    public byte[] captureScreen() {
        Image image = imageReader.acquireLatestImage();
        if (image == null) {
            return null;
        }
        int width = image.getWidth();
        int height = image.getHeight();
        final Image.Plane plane = image.getPlanes()[0];
        final ByteBuffer buffer = plane.getBuffer();
        // 相邻像素样本之间的距离，因为RGBA，所以间距是4个字节
        int pixelStride = plane.getPixelStride();
        // 每行的宽度
        int rowStride = plane.getRowStride();
        // 因为内存对齐问题，每个buffer宽度不同，所以通过pixelStride * width得到大概的宽度，
        // 然后通过rowStride去减，得到大概的内存偏移量，不过一般都是对齐的。
        int rowPadding = rowStride - pixelStride * width;
//        // 创建具体的bitmap，由于rowPadding是RGBA 4个通道的，所以也要除以pixelStride，得到实际的宽
//        Bitmap bitmap = Bitmap.createBitmap(width + rowPadding / pixelStride, height, Bitmap.Config.ARGB_8888);
//        bitmap.copyPixelsFromBuffer(buffer);
//        image.close();
//        return Bitmap.createBitmap(bitmap, 0, 0, width, height);
        // 创建存放像素数据的数组
        byte[] data = new byte[width * height * 4];
        int pos = 0, offset = 0;
        for (int i = 0; i < height; i++) {
            for (int j = 0; j < width; j++) {
                data[pos++] = buffer.get(offset + 2); // B
                data[pos++] = buffer.get(offset + 1); // G
                data[pos++] = buffer.get(offset);     // R
                data[pos++] = buffer.get(offset + 3); // A
                offset += pixelStride;
            }
            offset += rowPadding;
        }
        image.close();
        return data;
    }

    public void tap(float x, float y) {
        Path p = new Path();
        p.moveTo(x, y);
        GestureDescription gesture = new GestureDescription.Builder()
                .addStroke(new GestureDescription.StrokeDescription(p, 0, 1))
                .build();
        dispatchGesture(gesture, null, null);
    }

    public void swipe(float x1, float y1, float x2, float y2) {
        Path p = new Path();
        p.moveTo(x1, y1);
        p.lineTo(x2, y2);
        GestureDescription gesture = new GestureDescription.Builder()
                .addStroke(new GestureDescription.StrokeDescription(p, 0, 500))
                .build();
        dispatchGesture(gesture, null, null);
    }

    public void requestRecord(Runnable callback) {
        taskCallback = callback;
        Intent intent = new Intent(this, RequestRecordActivity.class);
        intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
        startActivity(intent);
    }

    public void onRequestResult(int resultCode, Intent data) {
        if (taskCallback == null) {
            return;
        }
        handler.post(() -> {
            startForeground(NOTIFICATION_ID,
                    new NotificationCompat.Builder(this, MainActivity.CHANNEL_ID).build());
            floatingButton.setImage(R.drawable.ic_stop_24);
            MediaProjectionManager mediaProjectionManager =
                    (MediaProjectionManager) getSystemService(Context.MEDIA_PROJECTION_SERVICE);
            mediaProjection = mediaProjectionManager.getMediaProjection(resultCode, data);
            int[] size = getScreenSize();
            imageReader = ImageReader.newInstance(size[0], size[1], PixelFormat.RGBA_8888, 2);
            virtualDisplay = mediaProjection.createVirtualDisplay(TAG, size[0], size[1], getScreenDpi(),
                    DisplayManager.VIRTUAL_DISPLAY_FLAG_AUTO_MIRROR, imageReader.getSurface(),
                    null, null);
            taskThread = new Thread(() -> {
                try {
                    Thread.sleep(500); // 刚开始获取不到截图
                    taskCallback.run();
                    handler.post(this::stopTask);
                } catch (InterruptedException ignored) {
                } catch (PyException e) {
                    if (!(e.getCause() instanceof InterruptedException)) {
                        throw e;
                    }
                }
            });
            taskThread.start();
        });
    }

    public void stopTask() {
        if (taskThread != null) {
            taskThread.interrupt();
            try {
                taskThread.join();
            } catch (InterruptedException ignored) {}
            taskThread = null;
            taskCallback = null;
        }
        if (virtualDisplay != null) {
            virtualDisplay.release();
            virtualDisplay = null;
        }
        if (imageReader != null) {
            imageReader.close();
            imageReader = null;
        }
        if (mediaProjection != null) {
            mediaProjection.stop();
            mediaProjection = null;
        }
        floatingButton.setImage(R.drawable.ic_flower_24);
        stopForeground(Service.STOP_FOREGROUND_REMOVE);
    }

    public void showMenu(String title, List<String> items, DialogInterface.OnClickListener listener) {
        AlertDialog menuDialog = new AlertDialog.Builder(this)
                .setTitle(title)
                .setItems(items.toArray(new String[0]), (dialog, which) -> {
                    if (which == items.size() - 1) {
                        disableSelf();
                        // HACK 禁用无障碍服务后Application未结束导致空指针异常
                        android.os.Process.killProcess(android.os.Process.myPid());
                    } else {
                        listener.onClick(dialog, which);
                    }
                })
                .setPositiveButton(R.string.back, (dialog, which) -> {
                    dialog.dismiss();
                })
                .create();
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            menuDialog.getWindow().setType(WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY);
        } else {
            menuDialog.getWindow().setType(WindowManager.LayoutParams.TYPE_SYSTEM_ALERT);
        }
        menuDialog.show();
    }
}
