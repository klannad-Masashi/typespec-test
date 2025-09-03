package com.example.userapi.dto;

import javax.validation.constraints.*;
import java.time.LocalDateTime;
import java.util.UUID;
import java.math.BigDecimal;
import java.util.List;

/**
 * UpdateUserRequest DTO
 * ユーザー更新リクエスト
 * TypeSpecから自動生成 - 2025-09-03T01:10:28.105171
 */
public class UpdateUserRequest {


    /**
     * ユーザー名
     */

    @Size(min=1, max=50)

    private String username;


    /**
     * メールアドレス
     */

    @Email

    private String email;


    /**
     * フルネーム
     */

    @Size(min=0, max=100)

    private String fullName;


    /**
     * アクティブフラグ
     */

    private Boolean isActive;



    // コンストラクタ
    public UpdateUserRequest() {}


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


    // isActive のgetter/setter
    public Boolean getIsactive() {
        return isActive;
    }

    public void setIsactive(Boolean isActive) {
        this.isActive = isActive;
    }


}