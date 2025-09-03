package com.example.userapi.dto;

import javax.validation.constraints.*;
import java.time.LocalDateTime;
import java.util.UUID;
import java.math.BigDecimal;
import java.util.List;

/**
 * UserListResponse DTO
 * ユーザー一覧レスポンス
 * TypeSpecから自動生成 - 2025-09-03T01:10:28.112520
 */
public class UserListResponse {


    /**
     * ユーザーリスト
     */

    @NotNull

    private List<String> users;


    /**
     * 総件数
     */

    @NotNull

    private Integer total;


    /**
     * 現在のページ
     */

    @NotNull

    private Integer page;


    /**
     * 1ページあたりの件数
     */

    @NotNull

    private Integer limit;



    // コンストラクタ
    public UserListResponse() {}


    // users のgetter/setter
    public List<String> getUsers() {
        return users;
    }

    public void setUsers(List<String> users) {
        this.users = users;
    }


    // total のgetter/setter
    public Integer getTotal() {
        return total;
    }

    public void setTotal(Integer total) {
        this.total = total;
    }


    // page のgetter/setter
    public Integer getPage() {
        return page;
    }

    public void setPage(Integer page) {
        this.page = page;
    }


    // limit のgetter/setter
    public Integer getLimit() {
        return limit;
    }

    public void setLimit(Integer limit) {
        this.limit = limit;
    }


}