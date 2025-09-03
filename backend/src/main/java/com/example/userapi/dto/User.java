package com.example.userapi.dto;

import javax.validation.constraints.*;
import java.time.LocalDateTime;
import java.util.UUID;
import java.math.BigDecimal;
import java.util.List;

/**
 * User DTO
 * ユーザー情報
 * TypeSpecから自動生成 - 2025-09-03T01:10:28.107685
 */
public class User {


    /**
     * ユーザーID（自動生成）
     */

    @NotNull

    private Integer id;


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


    /**
     * 作成日時
     */

    @NotNull

    private LocalDateTime createdAt;


    /**
     * 更新日時
     */

    @NotNull

    private LocalDateTime updatedAt;


    /**
     * アクティブフラグ
     */

    @NotNull

    private Boolean isActive;



    // コンストラクタ
    public User() {}


    // id のgetter/setter
    public Integer getId() {
        return id;
    }

    public void setId(Integer id) {
        this.id = id;
    }


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


    // createdAt のgetter/setter
    public LocalDateTime getCreatedat() {
        return createdAt;
    }

    public void setCreatedat(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }


    // updatedAt のgetter/setter
    public LocalDateTime getUpdatedat() {
        return updatedAt;
    }

    public void setUpdatedat(LocalDateTime updatedAt) {
        this.updatedAt = updatedAt;
    }


    // isActive のgetter/setter
    public Boolean getIsactive() {
        return isActive;
    }

    public void setIsactive(Boolean isActive) {
        this.isActive = isActive;
    }


}