package kongsang.swybot;

import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageInfo;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.provider.Settings;
import android.util.Log;

import androidx.activity.result.ActivityResultLauncher;
import androidx.activity.result.contract.ActivityResultContracts;
import androidx.appcompat.app.AlertDialog;
import androidx.appcompat.app.AppCompatActivity;

public class MainActivity extends AppCompatActivity {
    public static final String CHANNEL_ID = "SWY_BOT";
    private static final String TAG = "MainActivity";
    private static final String SWY_PACKAGE_NAME = "com.tencent.swy";

    private ActivityResultLauncher<Intent> activityResultLauncher;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            NotificationManager notificationManager =
                    (NotificationManager) getSystemService(Context.NOTIFICATION_SERVICE);
            NotificationChannel channel = new NotificationChannel(
                    CHANNEL_ID, getString(R.string.app_name), NotificationManager.IMPORTANCE_DEFAULT);
            notificationManager.createNotificationChannel(channel);
        }

        try {
            PackageInfo swyPackageInfo = getPackageManager().getPackageInfo(SWY_PACKAGE_NAME, 0);
            Log.i(TAG, "Found swy version: " + swyPackageInfo.versionName);
        } catch (PackageManager.NameNotFoundException e) {
            new AlertDialog.Builder(this)
                    .setMessage(R.string.exit_message)
                    .setPositiveButton(android.R.string.ok, (dialog, which) -> finish())
                    .setCancelable(false)
                    .show();
            return;
        }

        activityResultLauncher = registerForActivityResult(
                new ActivityResultContracts.StartActivityForResult(),
                result -> requestPermissions());
        requestPermissions();
    }

    private void requestPermissions() {
        if (!Settings.canDrawOverlays(this)) {
            new AlertDialog.Builder(this)
                    .setMessage(R.string.permission_window)
                    .setPositiveButton(android.R.string.ok, (dialog, which) -> {
                        activityResultLauncher.launch(new Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION,
                                Uri.parse("package:" + getPackageName())));
                    })
                    .setCancelable(false)
                    .show();
            return;
        }
        if (!SystemUtil.isAccessibilityEnabled(this, SwyBotService.class)) {
            new AlertDialog.Builder(this)
                    .setMessage(R.string.permission_accessibility)
                    .setPositiveButton(android.R.string.ok, (dialog, which) -> {
                        activityResultLauncher.launch(new Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS));
                    })
                    .setCancelable(false)
                    .show();
            return;
        }
        SystemUtil.toast(this, R.string.permission_ok);
        startSwyBot();
    }

    private void startSwyBot() {
        startService(new Intent(this, SwyBotService.class));
        startActivity(getPackageManager().getLaunchIntentForPackage(SWY_PACKAGE_NAME));
        finish();
    }
}
