package com.example

import android.annotation.SuppressLint
import android.graphics.Bitmap
import android.os.Bundle
import android.view.ViewGroup
import android.webkit.WebChromeClient
import android.webkit.WebResourceError
import android.webkit.WebResourceRequest
import android.webkit.WebSettings
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.activity.ComponentActivity
import androidx.activity.compose.BackHandler
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableFloatStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import com.example.ui.theme.MyApplicationTheme

class MainActivity : ComponentActivity() {
  override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    window.clearFlags(android.view.WindowManager.LayoutParams.FLAG_HARDWARE_ACCELERATED)
    enableEdgeToEdge()
    setContent {
      MyApplicationTheme {
        CalculusAppScreen()
      }
    }
  }
}

@SuppressLint("SetJavaScriptEnabled")
@Composable
fun CalculusAppScreen() {
  var webViewInstance by remember { mutableStateOf<WebView?>(null) }
  var canGoBack by remember { mutableStateOf(false) }
  var progress by remember { mutableFloatStateOf(0f) }
  var isLoading by remember { mutableStateOf(true) }

  BackHandler(enabled = canGoBack) {
    webViewInstance?.goBack()
  }

  Scaffold(
    modifier = Modifier
      .fillMaxSize()
      .background(Color(0xFF0B1329))
  ) { innerPadding ->
    Box(
      modifier = Modifier
        .fillMaxSize()
        .padding(innerPadding)
    ) {
      AndroidView(
        modifier = Modifier
          .fillMaxSize()
          .testTag("calculus_webview"),
        factory = { context ->
          WebView(context).apply {
            layoutParams = ViewGroup.LayoutParams(
              ViewGroup.LayoutParams.MATCH_PARENT,
              ViewGroup.LayoutParams.MATCH_PARENT
            )
            // Use software rendering to avoid MESA DRM rendernode errors in emulator/container
            setLayerType(android.view.View.LAYER_TYPE_SOFTWARE, null)
            setBackgroundColor(android.graphics.Color.parseColor("#0B1329"))

            settings.apply {
              javaScriptEnabled = true
              domStorageEnabled = true
              allowFileAccess = true
              allowContentAccess = true
              @Suppress("DEPRECATION")
              allowFileAccessFromFileURLs = true
              @Suppress("DEPRECATION")
              allowUniversalAccessFromFileURLs = true
              databaseEnabled = true
              useWideViewPort = true
              loadWithOverviewMode = true
              cacheMode = WebSettings.LOAD_DEFAULT
              mixedContentMode = WebSettings.MIXED_CONTENT_ALWAYS_ALLOW
            }

            webChromeClient = object : WebChromeClient() {
              override fun onProgressChanged(view: WebView?, newProgress: Int) {
                progress = newProgress / 100f
                isLoading = newProgress < 100
                canGoBack = view?.canGoBack() == true
              }
            }

            webViewClient = object : WebViewClient() {
              override fun onPageStarted(view: WebView?, url: String?, favicon: Bitmap?) {
                isLoading = true
                canGoBack = view?.canGoBack() == true
              }

              override fun onPageFinished(view: WebView?, url: String?) {
                isLoading = false
                canGoBack = view?.canGoBack() == true
              }

              override fun onReceivedError(
                view: WebView?,
                request: WebResourceRequest?,
                error: WebResourceError?
              ) {
                super.onReceivedError(view, request, error)
              }
            }

            loadUrl("file:///android_asset/index.html")
            webViewInstance = this
          }
        },
        update = {
          webViewInstance = it
        }
      )

      if (isLoading && progress < 1f) {
        LinearProgressIndicator(
          progress = { progress },
          modifier = Modifier
            .fillMaxWidth()
            .height(3.dp)
            .align(Alignment.TopCenter),
          color = Color(0xFF38BDF8),
          trackColor = Color(0xFF131D38),
        )
      }
    }
  }
}

@Composable
fun Greeting(name: String, modifier: Modifier = Modifier) {
  androidx.compose.material3.Text(text = "Hello $name!", modifier = modifier)
}
