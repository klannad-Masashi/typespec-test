package com.example.userapi.controller;

import org.springframework.web.bind.annotation.*;
import org.springframework.http.ResponseEntity;
import org.springframework.http.HttpStatus;
import org.springframework.beans.factory.annotation.Autowired;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import javax.validation.Valid;
import java.util.List;


import com.example.userapi.dto.CreateUserRequest;

import com.example.userapi.dto.DeleteResponse;

import com.example.userapi.dto.ErrorResponse;

import com.example.userapi.dto.UpdateUserRequest;

import com.example.userapi.dto.User;

import com.example.userapi.dto.UserCreateResponse;

import com.example.userapi.dto.UserListResponse;


/**
 * TypeSpecから自動生成されたAPIコントローラー
 * 生成日時: 2025-09-03T01:10:28.095593
 */
@RestController
@RequestMapping("/api")
@Tag(name = "User API", description = "ユーザー管理API")
public class UserController {

    // TODO: サービスクラスの注入
    // @Autowired
    // private UserService userService;

    /**
     * ユーザー一覧取得
     */
    @GetMapping("/users")
    @Operation(summary = "ユーザー一覧取得", description = "全ユーザーの一覧を取得します")
    public ResponseEntity<List<User>> getUsers() {
        // TODO: 実装
        return ResponseEntity.ok().build();
    }

    /**
     * ユーザー詳細取得
     */
    @GetMapping("/users/{id}")
    @Operation(summary = "ユーザー詳細取得", description = "指定されたIDのユーザー詳細を取得します")
    public ResponseEntity<User> getUserById(@PathVariable Long id) {
        // TODO: 実装
        return ResponseEntity.ok().build();
    }

    /**
     * ユーザー作成
     */
    @PostMapping("/users")
    @Operation(summary = "ユーザー作成", description = "新しいユーザーを作成します")
    public ResponseEntity<User> createUser(@Valid @RequestBody User user) {
        // TODO: 実装
        return ResponseEntity.status(HttpStatus.CREATED).build();
    }

    /**
     * ユーザー更新
     */
    @PutMapping("/users/{id}")
    @Operation(summary = "ユーザー更新", description = "指定されたIDのユーザー情報を更新します")
    public ResponseEntity<User> updateUser(@PathVariable Long id, @Valid @RequestBody User user) {
        // TODO: 実装
        return ResponseEntity.ok().build();
    }

    /**
     * ユーザー削除
     */
    @DeleteMapping("/users/{id}")
    @Operation(summary = "ユーザー削除", description = "指定されたIDのユーザーを削除します")
    public ResponseEntity<Void> deleteUser(@PathVariable Long id) {
        // TODO: 実装
        return ResponseEntity.noContent().build();
    }
}