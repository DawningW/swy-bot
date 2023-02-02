package kongsang.swybot;

import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.media.projection.MediaProjectionManager;
import android.os.Bundle;

public class RequestRecordActivity extends Activity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        MediaProjectionManager mediaProjectionManager =
                (MediaProjectionManager) getSystemService(Context.MEDIA_PROJECTION_SERVICE);
        Intent intent = mediaProjectionManager.createScreenCaptureIntent();
        startActivityForResult(intent, 233);
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        if (requestCode == 233 && resultCode == RESULT_OK) {
            ScriptBridge.getService().onRequestResult(resultCode, data);
        }
        finish();
    }
}
