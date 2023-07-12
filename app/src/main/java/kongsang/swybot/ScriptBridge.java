package kongsang.swybot;

import android.net.Uri;

import com.chaquo.python.PyObject;
import com.chaquo.python.Python;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.InputStream;
import java.util.stream.Collectors;

public class ScriptBridge {
    private static final Python python = Python.getInstance();
    private static PyObject main;
    private static SwyBotService botService;

    protected static PyObject getMainModule() {
        if (main == null) {
            main = python.getModule("main");
        }
        return main;
    }

    protected static void setService(SwyBotService service) {
        botService = service;
    }

    public static SwyBotService getService() {
        return botService;
    }

    public static void requestRecord(PyObject callback) {
        getService().requestRecord(callback::call);
    }

    public static void showMenu(PyObject title, PyObject items, PyObject callback) {
        botService.showMenu(
                title.toString(),
                items.asList()
                        .stream()
                        .map(PyObject::toString)
                        .collect(Collectors.toList()),
                (dialog, which) -> callback.call(which));
    }

    public static PyObject getStoragePath() {
        return PyObject.fromJava(getService().getExternalFilesDir(null).getPath());
    }

    public static PyObject saveToAlbum(PyObject from, PyObject to) {
        File file = new File(from.toString());
        try (InputStream is = new FileInputStream(file)) {
            Uri uri = MediaUtil.saveToAlbum(botService, is, "swybot", to.toString(), false);
            return PyObject.fromJava(uri != null);
        } catch (IOException e) {
            e.printStackTrace();
        }
        return PyObject.fromJava(false);
    }
}
