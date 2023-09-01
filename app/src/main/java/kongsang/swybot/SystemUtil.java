package kongsang.swybot;

import android.accessibilityservice.AccessibilityService;
import android.annotation.SuppressLint;
import android.content.Context;
import android.graphics.Bitmap;
import android.provider.Settings;
import android.text.TextUtils;
import android.util.Log;
import android.widget.Toast;

import androidx.annotation.StringRes;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.lang.reflect.Method;

public final class SystemUtil {
    private static final String TAG = "SystemUtil";

    private SystemUtil() {}

    @SuppressWarnings("SameParameterValue")
    public static boolean isAccessibilityEnabled(Context context, Class<? extends AccessibilityService> service) {
        try {
            if (Settings.Secure.getInt(context.getContentResolver(), Settings.Secure.ACCESSIBILITY_ENABLED, 0) != 1) {
                return false;
            }
            String services = Settings.Secure.getString(context.getContentResolver(), Settings.Secure.ENABLED_ACCESSIBILITY_SERVICES);
            if (!TextUtils.isEmpty(services)) {
                TextUtils.SimpleStringSplitter splitter = new TextUtils.SimpleStringSplitter(':');
                splitter.setString(services);
                while (splitter.hasNext()) {
                    if (splitter.next().equalsIgnoreCase(context.getPackageName() + "/" + service.getName())) {
                        return true;
                    }
                }
            }
        } catch (Throwable e) {
            Log.e(TAG, "isAccessibilityEnabled: ", e);
        }
        return false;
    }

    public static int dip2px(Context context, float dp) {
        float scale = context.getResources().getDisplayMetrics().density;
        return Math.round(dp * scale + 0.5f);
    }

    public static void toast(Context context, String msg) {
        Toast.makeText(context, msg, msg.length() > 10 ? Toast.LENGTH_LONG : Toast.LENGTH_SHORT)
                .show();
    }

    public static void toast(Context context, @StringRes int resId) {
        toast(context, context.getString(resId));
    }

    public static void saveBitmap(Context context, String name, Bitmap bitmap) {
        File file = new File(context.getExternalFilesDir(null), name);
        try {
            FileOutputStream stream = new FileOutputStream(file);
            bitmap.compress(Bitmap.CompressFormat.PNG, 0, stream);
            stream.flush();
            stream.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public static boolean isHarmonyOS() {
        try {
            Class<?> clz = Class.forName("com.huawei.system.BuildEx");
            Method method = clz.getMethod("getOsBrand");
            String ret = (String) method.invoke(clz);
            return "harmony".equals(ret);
        } catch (Exception e) {
            e.printStackTrace();
        }
        return false;
    }

    @SuppressLint("PrivateApi")
    public static int getHarmonyVersion() {
        try {
            Class<?> clz = Class.forName("android.os.SystemProperties");
            Method method = clz.getDeclaredMethod("get", String.class);
            String ret = (String) method.invoke(clz, "hw_sc.build.platform.version");
            if (!TextUtils.isEmpty(ret)) {
                return Integer.parseInt(ret.split("\\.")[0]);
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        return 0;
    }
}
