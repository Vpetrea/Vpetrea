package com.vpetrea.checksplit

import android.animation.ArgbEvaluator
import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.text.Editable
import android.text.TextWatcher
import android.util.Log
import android.widget.EditText
import android.widget.SeekBar
import android.widget.TextView
import androidx.core.content.ContextCompat

private const val TAG = "MainActivity"
private const val INITAL_TIP = 15
class MainActivity : AppCompatActivity() {
    private lateinit var etBaseAmount: EditText
    private lateinit var sbTip: SeekBar
    private lateinit var tvTipDisplay: TextView
    private lateinit var tvPercent: TextView
    private lateinit var tvTotalDisplay: TextView
    private lateinit var tvTipDescription: TextView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        etBaseAmount = findViewById(R.id.etBaseAmount)
        sbTip = findViewById(R.id.sbTip)
        tvTipDisplay = findViewById(R.id.tvTipDisplay)
        tvTotalDisplay = findViewById(R.id.tvTotalDisplay)
        tvPercent = findViewById(R.id.tvPercent)
        tvTipDescription = findViewById(R.id.tvTipDiscription)


        sbTip.progress = INITAL_TIP
        tvPercent.text = "$INITAL_TIP%"
        updateTipDescription(INITAL_TIP)
        sbTip.setOnSeekBarChangeListener(object: SeekBar.OnSeekBarChangeListener{
            override fun onProgressChanged(seekBar: SeekBar?, progress: Int, fromUser: Boolean) {
                Log.i(TAG,"onProgressChanged $progress")
                tvPercent.text = "$progress%"
                computeTipandTotal()
                updateTipDescription(progress)
            }

            override fun onStartTrackingTouch(p0: SeekBar?) {}

            override fun onStopTrackingTouch(p0: SeekBar?) {}

        })
        etBaseAmount.addTextChangedListener(object: TextWatcher{
            override fun beforeTextChanged(p0: CharSequence?, p1: Int, p2: Int, p3: Int) {}

            override fun onTextChanged(p0: CharSequence?, p1: Int, p2: Int, p3: Int) {}

            override fun afterTextChanged(p0: Editable?) {
                Log.i(TAG,"afterTextChanged $p0")
                computeTipandTotal()
            }

        })
    }

    private fun updateTipDescription(tipPercent: Int) {
        val tipDescription = when (tipPercent) {
            in 0..9 -> "Poor"
            in 10..14 -> "Acceptable"
            in 15..19 -> "Good"
            in 20..24 -> "Great"
            else -> "Amazing"
        }
        tvTipDescription.text = tipDescription

        val color = ArgbEvaluator().evaluate(
            tipPercent.toFloat() / sbTip.max,
            ContextCompat.getColor(this, R.color.color_worst),
            ContextCompat.getColor(this, R.color.color_best)
        ) as Int
        tvTipDescription.setTextColor(color)
    }

    private fun computeTipandTotal() {
        if (etBaseAmount.text.isEmpty()){
            tvTipDisplay.text = ""
            tvTotalDisplay.text = ""
            return
        }
        val baseamount = etBaseAmount.text.toString().toDouble()
        val tip = sbTip.progress
        val tipamount = baseamount * tip / 100
        val total = baseamount + tipamount
        tvTipDisplay.text = "%.2f".format(tipamount)
        tvTotalDisplay.text = "%.2f".format(total)

    }
}