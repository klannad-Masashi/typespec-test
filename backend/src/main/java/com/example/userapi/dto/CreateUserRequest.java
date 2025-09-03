package com.example.userapi.dto;

import javax.validation.constraints.*;
import java.time.LocalDateTime;
import java.util.UUID;
import java.math.BigDecimal;
import java.util.List;

/**
 * CreateUserRequest DTO
 * ユーザー作成リクエスト
 * TypeSpecから自動生成 - 2025-09-03T01:10:28.098190
 */
public class CreateUserRequest {


    /**
     * ユーザー名
     */

    @NotNull

    @Size(min=1, max=50)

    private String username;


    /**
     * メールアドレス
     */

    @NotNull

    @Email

    private String email;


    /**
     * フルネーム
     */

    @NotNull

    @Size(min=0, max=100)

    private String fullName;



    // コンストラクタ
    public CreateUserRequest() {}


    // username のgetter/setter
    public String getUsername() {
        return username;
    }

    public void setUsername(String username) {
        this.username = username;
    }


    // email のgetter/setter
    public String getEmail() {
        return email;
    }

    public void setEmail(String email) {
        this.email = email;
    }


    // fullName のgetter/setter
    public String getFullname() {
        return fullName;
    }

    public void setFullname(String fullName) {
        this.fullName = fullName;
    }


}