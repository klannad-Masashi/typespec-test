package com.example.userapi.dto;

import javax.validation.constraints.*;
import java.time.LocalDateTime;
import java.util.UUID;
import java.math.BigDecimal;
import java.util.List;

/**
 * UserCreateResponse DTO
 * ユーザー作成レスポンス
 * TypeSpecから自動生成 - 2025-09-03T01:10:28.110112
 */
public class UserCreateResponse {


    /**
     * 作成されたユーザー
     */

    @NotNull

    private String user;



    // コンストラクタ
    public UserCreateResponse() {}


    // user のgetter/setter
    public String getUser() {
        return user;
    }

    public void setUser(String user) {
        this.user = user;
    }


}