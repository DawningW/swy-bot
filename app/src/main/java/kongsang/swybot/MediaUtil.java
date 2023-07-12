package kongsang.swybot;

import android.annotation.TargetApi;
import android.content.ContentResolver;
import android.content.ContentUris;
import android.content.ContentValues;
import android.content.Context;
import android.content.Intent;
import android.database.Cursor;
import android.net.Uri;
import android.os.Build;
import android.os.Environment;
import android.provider.MediaStore;
import android.text.TextUtils;
import android.util.Log;

import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;

import kotlin.io.FilesKt;

/**
 * From https://github.com/hushenghao/MediaStoreDemo
 */
public final class MediaUtil {
    private static final String TAG = "MediaUtil";
    private static final String ALBUM_DIR = Environment.DIRECTORY_PICTURES;

    private MediaUtil() {}

    /**
     * 保存图片或视频 Stream 到 Pictures 的指定文件夹
     *
     * @param context 上下文
     * @param inputStream 媒体文件的输入流
     * @param fileName 包含后缀名的完整文件名
     * @param relativePath 文件相对于 Pictures 的路径
     * @param isVideo 是否为视频
     * @return 保存后文件的 uri
     */
    public static Uri saveToAlbum(Context context, InputStream inputStream, String relativePath, String fileName, boolean isVideo) {
        ContentResolver resolver = context.getContentResolver();
        File[] outputFile = new File[1];
        Uri uri = insertMediaItem(resolver, relativePath, fileName, isVideo, outputFile);
        if (uri == null) {
            Log.e(TAG, "Insert media error: uri is null!");
            return null;
        }
        try (OutputStream outputStream = resolver.openOutputStream(uri)) {
            byte[] buffer = new byte[8 * 1024];
            int nread;
            while ((nread = inputStream.read(buffer)) != -1) {
                outputStream.write(buffer, 0, nread);
            }
        } catch (IOException e) {
            Log.e(TAG, e.getMessage());
            return null;
        }
        finishPending(context, resolver, uri, outputFile[0]);
        return uri;
    }

    /**
     * 根据文件名获取 MimeType
     *
     * @param fileName 文件名
     * @return MimeType
     */
    private static String getMimeType(String fileName) {
        fileName = fileName.toLowerCase();
        if (fileName.endsWith(".png")) {
            return "image/png";
        } else if (fileName.endsWith(".jpg") || fileName.endsWith(".jpeg")) {
            return "image/jpeg";
        } else if (fileName.endsWith(".webp")) {
            return "image/webp";
        } else if (fileName.endsWith(".gif")) {
            return "image/gif";
        } else if (fileName.endsWith(".mp4")) {
            return "video/mp4";
        }
        return null;
    }

    /**
     * 插入图片或视频到媒体库
     *
     * @param resolver ContentResolver
     * @param relativePath 相对路径
     * @param fileName 文件名
     * @param isVideo 是否为视频
     * @param outputFile 返回插入的媒体文件 (Android Q 以下有效)
     * @return 插入的媒体的 uri
     */
    private static Uri insertMediaItem(ContentResolver resolver, String relativePath, String fileName, boolean isVideo, File[] outputFile) {
        // 媒体信息
        ContentValues contentValues = new ContentValues();
        String mimeType = getMimeType(fileName);
        if (mimeType != null) {
            contentValues.put(MediaStore.MediaColumns.MIME_TYPE, mimeType);
        }
        long timestamp = System.currentTimeMillis() / 1000;
        contentValues.put(MediaStore.MediaColumns.DATE_ADDED, timestamp);
        contentValues.put(MediaStore.MediaColumns.DATE_MODIFIED, timestamp);
        // 保存的位置
        Uri collection;
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            String path = ALBUM_DIR;
            if (!TextUtils.isEmpty(relativePath)) {
                path += "/" + relativePath;
            }
            contentValues.put(MediaStore.MediaColumns.DISPLAY_NAME, fileName);
            contentValues.put(MediaStore.MediaColumns.RELATIVE_PATH, path);
            contentValues.put(MediaStore.MediaColumns.IS_PENDING, 1);
            collection = isVideo ? MediaStore.Video.Media.getContentUri(MediaStore.VOLUME_EXTERNAL_PRIMARY)
                            : MediaStore.Images.Media.getContentUri(MediaStore.VOLUME_EXTERNAL_PRIMARY);
            // 高版本不用查重直接插入，会自动重命名
        } else {
            File saveDir = Environment.getExternalStoragePublicDirectory(ALBUM_DIR);
            if (!TextUtils.isEmpty(relativePath)) {
                saveDir = new File(saveDir, relativePath);
            }
            if (!saveDir.exists() && !saveDir.mkdirs()) {
                Log.e(TAG, "Save media error: can't create Pictures directory!");
                return null;
            }
            // 文件路径查重，重复的话在文件名后拼接数字
            File file = new File(saveDir, fileName);
            String fileNameWithoutExtension = FilesKt.getNameWithoutExtension(file);
            String fileExtension = FilesKt.getExtension(file);
            int suffix = 1;
            while (queryMediaItem28(resolver, file.getAbsolutePath(), isVideo) != null) {
                String newName = fileNameWithoutExtension + " (" + suffix++ + ")." + fileExtension;
                file = new File(saveDir, newName);
            }
            contentValues.put(MediaStore.MediaColumns.DISPLAY_NAME, file.getName());
            // 保存路径
            contentValues.put(MediaStore.MediaColumns.DATA, file.getAbsolutePath());
            outputFile[0] = file; // 回传文件路径，用于设置文件大小
            collection = isVideo ? MediaStore.Video.Media.EXTERNAL_CONTENT_URI
                            : MediaStore.Images.Media.EXTERNAL_CONTENT_URI;
        }
        // 插入图片信息
        return resolver.insert(collection, contentValues);
    }

    /**
     * Android Q 以下版本，查询媒体库中当前路径是否存在
     *
     * @param resolver ContentResolver
     * @param path 文件路径
     * @param isVideo 是否为视频
     * @return Uri 返回 null 时说明不存在，可以执行图片插入逻辑
     */
    @TargetApi(Build.VERSION_CODES.P)
    private static Uri queryMediaItem28(ContentResolver resolver, String path, boolean isVideo) {
        File file = new File(path);
        if (file.canRead() && file.exists()) {
            return Uri.fromFile(file);
        }
        // 保存的位置
        Uri collection = isVideo ? MediaStore.Video.Media.EXTERNAL_CONTENT_URI
                            : MediaStore.Images.Media.EXTERNAL_CONTENT_URI;
        // 查询是否已经存在相同图片
        try (Cursor query = resolver.query(
                collection,
                new String[] {MediaStore.MediaColumns._ID, MediaStore.MediaColumns.DATA},
                MediaStore.MediaColumns.DATA + " == ?",
                new String[] {path},
                null)) {
            while (query.moveToNext()) {
                int idColumn = query.getColumnIndexOrThrow(MediaStore.MediaColumns._ID);
                long id = query.getLong(idColumn);
                Uri existsUri = ContentUris.withAppendedId(collection, id);
                return existsUri;
            }
        }
        return null;
    }

    /**
     * 通知媒体库更新
     *
     * @param context 上下文
     * @param resolver ContentResolver
     * @param uri 媒体的 uri
     * @param outputFile 媒体文件 (Android Q 以下有效)
     */
    private static void finishPending(Context context, ContentResolver resolver, Uri uri, File outputFile) {
        ContentValues contentValues = new ContentValues();
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.Q) {
            if (outputFile != null) {
                contentValues.put(MediaStore.MediaColumns.SIZE, outputFile.length());
            }
            resolver.update(uri, contentValues, null, null);
            // 通知媒体库更新
            Intent intent = new Intent(Intent.ACTION_MEDIA_SCANNER_SCAN_FILE, uri);
            context.sendBroadcast(intent);
        } else {
            // Android Q 添加了 IS_PENDING 状态，为 0 时其他应用才可见
            contentValues.put(MediaStore.MediaColumns.IS_PENDING, 0);
            resolver.update(uri, contentValues, null, null);
        }
    }
}
