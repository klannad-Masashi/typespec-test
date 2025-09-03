package com.example.userapi.dto;

import javax.validation.constraints.*;
import java.time.LocalDateTime;
import java.util.UUID;
import java.math.BigDecimal;
import java.util.List;

/**
 * DeleteResponse DTO
 * 削除成功レスポンス
 * TypeSpecから自動生成 - 2025-09-03T01:10:28.100590
 */
public class DeleteResponse {


    /**
     * 削除成功
     */

    private String message;



    // コンストラクタ
    public DeleteResponse() {}


    // message のgetter/setter
    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }


}