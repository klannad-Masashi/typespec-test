package com.example.userapi.dto;

import javax.validation.constraints.*;
import java.time.LocalDateTime;
import java.util.UUID;
import java.math.BigDecimal;
import java.util.List;

/**
 * ErrorResponse DTO
 * エラーレスポンス
 * TypeSpecから自動生成 - 2025-09-03T01:10:28.102877
 */
public class ErrorResponse {


    /**
     * エラーコード
     */

    @NotNull

    private String code;


    /**
     * エラーメッセージ
     */

    @NotNull

    private String message;


    /**
     * 詳細情報
     */

    private String details;



    // コンストラクタ
    public ErrorResponse() {}


    // code のgetter/setter
    public String getCode() {
        return code;
    }

    public void setCode(String code) {
        this.code = code;
    }


    // message のgetter/setter
    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }


    // details のgetter/setter
    public String getDetails() {
        return details;
    }

    public void setDetails(String details) {
        this.details = details;
    }


}